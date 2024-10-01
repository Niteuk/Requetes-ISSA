import json
import logging
import logging.config
import requests
import time
import yaml
from pprint import pformat
from traceback import format_exc
from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Cache to avoid redundant API requests
article_cache = {}


def load_config(config_file):
    with open(config_file, "r") as cfg:
        return yaml.safe_load(cfg)


# Load configuration
config = load_config("config/Data_request/requests.yaml")

# Configure logging
with open("config/logging.yaml", "rt") as f:
    config_log = yaml.safe_load(f.read())
    logging.config.dictConfig(config_log)
    logger = logging.getLogger(__name__)

ERROR_404 = "Error HTTP status 404"
ERROR_OTHER = "Other error"


def fetch_doi_list():
    """
    Fetch DOI list from SPARQL endpoint
    Returns:
        dict: dictionary with DOI as key and document URI as value
    """
    logger.info("Fetching DOI list from SPARQL endpoint")
    sparql = SPARQLWrapper(config["issa_sparql_endpoint"]["endpoint_url"])
    sparql.setQuery(config["issa_sparql_endpoint"]["query"])
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return {
        result["doi"]["value"]: result["document"]["value"]
        for result in results["results"]["bindings"]
    }


def fetch_article(identifier):
    """
    Fetch article info from the OpenAlex API

    Args:
        identifier (str): article identifier, DOI or OpenAlex id

    Returns:
        dict: article information (JSON response from OpenAlex API)
    """

    if "openalex.org" in identifier:
        _identifier = identifier
    else:
        _identifier = f"https://doi.org/{identifier}"
    logger.debug(f"Fetching info for article {_identifier}")

    if _identifier in article_cache:
        return article_cache[_identifier]

    url = f"{config['openalex_api']['base_url']}{_identifier}"
    if config["openalex_api"]["use_mailto"]:
        url += f"?mailto={config['openalex_api']['mailto_param']}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        article_cache[_identifier] = response.json()
        return article_cache[_identifier]

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.warning("Rate limit reached. Sleeping for 20 seconds...")
            time.sleep(20)
            # TODO: manage max number of attempts
            return fetch_article(identifier)
        elif e.response.status_code == 404:
            return ERROR_404
        else:
            logger.warning(f"Error fetching article {_identifier}: {e}")
            return ERROR_OTHER
    except requests.exceptions.RequestException as e:
        logger.warning(f"Request failed for article {_identifier}: {e}")
        return ERROR_OTHER


def extract_article_data(article_info):
    """
    Extract some data from OpenAlex data while ignoring non relevant data

    Args:
        article_info (dict): article information from OpenAlex API

    Returns:
        dict: reshaped relevant article info
    """
    if article_info in [ERROR_404, ERROR_OTHER]:
        return None
    try:
        article_data = {
            "Title": article_info["title"],
            "Publication Date": article_info.get("publication_date", ""),
            "DOI": article_info["doi"],
            "Cited_works": article_info.get("referenced_works", []),
            "Topics": [
                {
                    "Name": topic["display_name"],
                    "Score": topic.get("score", None),
                    "ID": topic.get("id", None),
                    "Subfield": {
                        "Name": (
                            topic["subfield"]["display_name"]
                            if "subfield" in topic
                            else None
                        ),
                        "ID": topic["subfield"]["id"] if "subfield" in topic else None,
                    },
                    "Field": {
                        "Name": (
                            topic["field"]["display_name"] if "field" in topic else None
                        ),
                        "ID": topic["field"]["id"] if "field" in topic else None,
                    },
                    "Domain": {
                        "Name": (
                            topic["domain"]["display_name"]
                            if "domain" in topic
                            else None
                        ),
                        "ID": topic["domain"]["id"] if "domain" in topic else None,
                    },
                }
                for topic in article_info.get("topics", [])
            ],
        }
        return article_data
    except KeyError as e:
        logger.error(f"Error extracting data: {e}")
        logger.error(format_exc())
        return None


def process_doi(doi):
    """
    Process a DOI: retrieve data from OpenAlex for an article given by its DOI,
    as well as data for the cited articles

    Args:
        doi (str): article identifier

    Returns:
        tuple: error message if any, article data
    """
    article_info = fetch_article(doi)
    if article_info:
        if article_info in [ERROR_404, ERROR_OTHER]:
            return article_info, None

        article_data = extract_article_data(article_info)
        if article_data:
            # Get data of cited articles
            cited_articles_data = []
            logger.info(
                f"Fetching data for {len(article_data['Cited_works'])} cited articles"
            )
            for cited_work in article_data["Cited_works"]:
                cited_article_info = fetch_article(cited_work)
                if cited_article_info and cited_article_info not in [
                    ERROR_404,
                    ERROR_OTHER,
                ]:
                    cited_article_data = extract_article_data(cited_article_info)
                    if cited_article_data:
                        # No need to keep the cited works of a cited article
                        cited_article_data.pop("Cited_works")
                        cited_articles_data.append(cited_article_data)
            article_data["Cited_articles"] = cited_articles_data
            return None, article_data
    return None, None


if __name__ == "__main__":

    # Initialize counters and article data list
    articles_data = []
    error_404_count = 0
    other_error_count = 0
    missing_info_count = 0

    # Fetch DOI list and their URIs
    doi_dict = fetch_doi_list()
    logger.info(f"Retrieved {len(doi_dict)} DOI and document URI pairs")

    if config["openalex_api"]["use_mailto"]:
        # Parralel execution with ThreadPoolExecutor
        with ThreadPoolExecutor(
            max_workers=config["openalex_api"]["max_workers"]
        ) as executor:
            future_to_doi = {
                executor.submit(process_doi, doi): doi for doi in doi_dict.keys()
            }
            for future in tqdm(as_completed(future_to_doi), total=len(doi_dict)):
                doi = future_to_doi[future]
                try:
                    error, article_data = future.result()
                    if error == ERROR_404:
                        error_404_count += 1
                    elif error == ERROR_OTHER:
                        other_error_count += 1
                    elif article_data:
                        article_data["Document URI"] = doi_dict[doi]
                        # Ajoute l'URI du document à l'article
                        if (
                            not article_data["Cited_articles"]
                            or not article_data["Topics"]
                        ):
                            missing_info_count += 1
                        else:
                            articles_data.append(article_data)
                            logger.info(
                                f"Data for DOI {doi} recorded with URI {doi_dict[doi]}."
                            )
                except Exception as exc:
                    logger.error(f"Exception while processing DOI {doi} : {exc}")
    else:
        # Sequential execution
        for doi in tqdm(doi_dict.keys()):
            error, article_data = process_doi(doi)
            if article_data:
                if error == ERROR_404:
                    error_404_count += 1
                elif error == ERROR_OTHER:
                    other_error_count += 1
                elif article_data:
                    article_data["Document URI"] = doi_dict[doi]
                    # Ajoute l'URI du document à l'article
                    if not article_data["Cited_articles"] or not article_data["Topics"]:
                        missing_info_count += 1
                    else:
                        articles_data.append(article_data)
                        logger.info(
                            f"Data for DOI {doi} recorded with URI {doi_dict[doi]}."
                        )

    # Save results to JSON file
    output = config["output_paths"]["article_data_interdisciplinarity"]
    with open(output, "w", encoding="utf-8") as jsonfile:
        json.dump(articles_data, jsonfile, ensure_ascii=False, indent=4)

    # Log summary information
    logger.info(f"Data saved in {output}")
    logger.info(f"Number of articles recorded: {len(articles_data)}")
    logger.info(f"Number of 404 errors: {error_404_count}")
    logger.info(f"Number of other errors: {other_error_count}")
    logger.info(f"Number of articles with missing info: {missing_info_count}")
