import requests
import json
import time
import logging
import logging.config
import yaml
from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load logging configuration from YAML
with open("config/logging.yaml", "rt") as f:
    config_log = yaml.safe_load(f.read())
    logging.config.dictConfig(config_log)
    logger = logging.getLogger(__name__)


# Load configuration from YAML
def load_config(config_file):
    """Load configuration from the given YAML file."""
    logger.debug(f"Loading configuration from {config_file}")
    with open(config_file, "r") as cfg:
        return yaml.safe_load(cfg)


config = load_config("config/Data_Request/requests.yaml")


# Fetch DOI list from SPARQL endpoint
def fetch_doi_list():
    """Fetch DOI list from the SPARQL endpoint."""
    sparql = SPARQLWrapper(config["SPARQL"]["endpoint_url"])
    sparql.setQuery(config["SPARQL"]["query"])
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [result["doi"]["value"] for result in results["results"]["bindings"]]


# Cache to avoid repeated requests
article_cache = {}


# Fetch article info from OpenAlex API
def fetch_article_info(doi):
    """Fetch article info from the OpenAlex API."""
    full_doi = f"https://doi.org/{doi}"
    if full_doi in article_cache:
        return article_cache[full_doi]

    base_url = config["API"]["base_url"]
    if config["API"]["use_mailto"]:
        url = f"{base_url}{full_doi}?mailto={config['API']['mailto_param']}"
    else:
        url = f"{base_url}{full_doi}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        article_cache[full_doi] = response.json()
        return article_cache[full_doi]
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.warning("Rate limit reached. Sleeping for 20 seconds...")
            time.sleep(20)
            return fetch_article_info(doi)
        elif e.response.status_code == 404:
            return "Error 404"
        else:
            logger.error(f"Error fetching DOI {full_doi}: {e}")
            return "Other error"
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for DOI {full_doi}: {e}")
        return "Other error"


# Extract relevant data from article info
def extract_article_data(article_info):
    """Extract relevant data from the article info."""
    if article_info in ["Error 404", "Other error"]:
        return None
    try:
        article_data = {
            "Title": article_info.get("title", "No title"),
            "Publication Date": article_info.get("publication_date", ""),
            "DOI": article_info.get("doi", ""),
            "Authors": [
                f"{authorship['author']['display_name']} (ORCID: {authorship['author'].get('orcid', 'No ORCID')})"
                for authorship in article_info.get("authorships", [])
            ],
            "Affiliations": list(
                {
                    f"{institution.get('display_name', 'No institution')} (ROR: {institution.get('ror', 'No ROR')})"
                    for authorship in article_info.get("authorships", [])
                    for institution in authorship.get("institutions", [])
                }
            ),
            "OpenAlex ID": article_info["id"],
            "SDGs": [
                {
                    "ID": sdg["id"],
                    "Name": sdg["display_name"],
                    "Score": sdg.get("score", None),
                }
                for sdg in article_info.get("sustainable_development_goals", [])
            ],
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
        return None


# Process DOI: fetch and extract data
def process_doi(doi):
    """Process a DOI to fetch and extract data."""
    article_info = fetch_article_info(doi)
    if article_info:
        if article_info == "Error 404":
            return "Error 404", None
        elif article_info == "Other error":
            return "Other error", None
        article_data = extract_article_data(article_info)
        if article_data:
            return None, article_data
    return None, None


# Main execution
if __name__ == "__main__":
    articles_data = []
    error_404_count = 0
    other_error_count = 0

    # Fetch DOI list
    doi_list = fetch_doi_list()
    logger.info(f"Total DOIs retrieved: {len(doi_list)}")

    if config["API"]["use_mailto"]:
        with ThreadPoolExecutor(max_workers=config["API"]["max_workers"]) as executor:
            future_to_doi = {executor.submit(process_doi, doi): doi for doi in doi_list}
            for future in tqdm(as_completed(future_to_doi), total=len(doi_list)):
                doi = future_to_doi[future]
                try:
                    error, article_data = future.result()
                    if error == "Error 404":
                        error_404_count += 1
                    elif error == "Other error":
                        other_error_count += 1
                    elif article_data:
                        articles_data.append(article_data)
                        logger.debug(f"Data for DOI {doi} recorded.")
                except Exception as exc:
                    logger.error(f"DOI {doi} generated an exception: {exc}")
    else:
        for doi in tqdm(doi_list):
            error, article_data = process_doi(doi)
            if error == "Error 404":
                error_404_count += 1
            elif error == "Other error":
                other_error_count += 1
            elif article_data:
                articles_data.append(article_data)
                logger.debug(f"Data for DOI {doi} recorded.")

    # Save data to JSON
    output_path = config["output_paths"]["article_data"]
    with open(output_path, "w", encoding="utf-8") as jsonfile:
        json.dump(articles_data, jsonfile, ensure_ascii=False, indent=4)

    # Print summary
    logger.info(f"Data saved in {output_path}.")
    logger.info(f"Number of articles recorded: {len(articles_data)}")
    logger.info(f"Number of 404 errors: {error_404_count} (not found)")
    logger.info(f"Number of other errors: {other_error_count}")
