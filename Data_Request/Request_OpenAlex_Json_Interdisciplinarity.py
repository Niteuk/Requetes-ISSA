import requests
import json
import time
import logging
import logging.config
import yaml
from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


# Load YAML configuration
def load_config(config_file):
    with open(config_file, "r") as cfg:
        return yaml.safe_load(cfg)


# Load configuration from YAML
config = load_config("config/Data_request/requests.yaml")

# Configure logging from a YAML file
with open("config/logging.yaml", "rt") as f:
    config_log = yaml.safe_load(f.read())
    logging.config.dictConfig(config_log)
    logger = logging.getLogger(__name__)

# Use the config file parameters
USE_MAILTO = config["API"]["use_mailto"]
MAILTO_PARAM = config["API"]["mailto_param"]
MAX_WORKERS = config["API"]["max_workers"]


# Function to fetch DOI list from SPARQL endpoint
def fetch_doi_list():
    """Fetch DOI list from SPARQL endpoint"""

    logger.info("Fetching DOI list from SPARQL endpoint")
    sparql = SPARQLWrapper(config["SPARQL"]["endpoint_url"])
    sparql.setQuery(config["SPARQL"]["query"])
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    # Return a dictionary with DOI as key and document URI as value
    return {
        result["doi"]["value"]: result["document"]["value"]
        for result in results["results"]["bindings"]
    }


# Cache to avoid redundant API requests
article_cache = {}


# Function to fetch article info from OpenAlex API
def fetch_article_info(doi):
    """Fetch article info from OpenAlex API"""

    full_doi = f"https://doi.org/{doi}"
    if full_doi in article_cache:
        return article_cache[full_doi]

    if USE_MAILTO:
        url = f"https://api.openalex.org/works/{full_doi}?mailto={MAILTO_PARAM}"
    else:
        url = f"https://api.openalex.org/works/{full_doi}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        article_cache[full_doi] = response.json()
        return article_cache[full_doi]
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print(
                "Rate limit reached. Sleeping for 20 seconds..."
                if USE_MAILTO
                else "Rate limit reached. Sleeping for 10 seconds..."
            )
            time.sleep(20 if USE_MAILTO else 10)
            return fetch_article_info(doi)
        elif e.response.status_code == 404:
            return "Error 404"
        else:
            print(f"Error fetching DOI {full_doi}: {e}")
            return "Other error"
    except requests.exceptions.RequestException as e:
        print(f"Request failed for DOI {full_doi}: {e}")
        return "Other error"


# Extract relevant data from the article
def extract_article_data(article_info):
    """Extract relevant data from the article"""
    if article_info in ["Error 404", "Other error"]:
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
        return None


# Process a DOI to extract article data
def process_doi(doi):
    """Process a DOI to extract article data"""
    article_info = fetch_article_info(doi)
    if article_info:
        if article_info == "Error 404":
            return "Error 404", None
        elif article_info == "Other error":
            return "Other error", None
        article_data = extract_article_data(article_info)
        if article_data:
            # Récupérer les données pour chaque article cité
            cited_articles_data = []
            for cited_work in article_data["Cited_works"]:
                cited_article_info = fetch_article_info(cited_work)
                if cited_article_info and cited_article_info not in [
                    "Error 404",
                    "Other error",
                ]:
                    cited_article_data = extract_article_data(cited_article_info)
                    if cited_article_data:
                        cited_articles_data.append(cited_article_data)
            article_data["Cited_articles"] = cited_articles_data
            return None, article_data
    return None, None


# Initialize counters and article data list
articles_data = []
error_404_count = 0
other_error_count = 0
missing_info_count = 0

# Fetch DOI list and their URIs
doi_dict = fetch_doi_list()
logger.info(f"Retrieved {len(doi_dict)} DOI and document URI pairs")

# Track worker threads
logger.info(f"Running with {MAX_WORKERS} workers.")

# Execute in multi-threaded mode if USE_MAILTO is True
if USE_MAILTO:
    # Utilisation de ThreadPoolExecutor pour les requêtes parallèles
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_doi = {
            executor.submit(process_doi, doi): doi for doi in doi_dict.keys()
        }
        for future in tqdm(as_completed(future_to_doi), total=len(doi_dict)):
            doi = future_to_doi[future]
            try:
                error, article_data = future.result()
                if error == "Error 404":
                    error_404_count += 1
                elif error == "Other error":
                    other_error_count += 1
                elif article_data:
                    article_data["Document URI"] = doi_dict[
                        doi
                    ]  # Ajoute l'URI du document à l'article
                    if not article_data["Cited_articles"] or not article_data["Topics"]:
                        missing_info_count += 1
                    else:
                        articles_data.append(article_data)
                        print(f"Data for DOI {doi} recorded with URI {doi_dict[doi]}.")
            except Exception as exc:
                print(f"DOI {doi} generated an exception: {exc}")
else:
    # Exécution séquentielle des requêtes
    for doi in tqdm(doi_dict.keys()):
        article_info = fetch_article_info(doi)
        if article_info:
            if article_info == "Error 404":
                error_404_count += 1
                continue
            elif article_info == "Other error":
                other_error_count += 1
                continue
            article_data = extract_article_data(article_info)
            if article_data:
                article_data["Document URI"] = doi_dict[
                    doi
                ]  # Ajoute l'URI du document à l'article
                if not article_data["Cited_articles"] or not article_data["Topics"]:
                    missing_info_count += 1
                else:
                    articles_data.append(article_data)
                    print(f"Data for DOI {doi} recorded with URI {doi_dict[doi]}.")

# Save results to JSON file
output_path = config["output_paths"]["article_data_interdisciplinarity"]
with open(output_path, "w", encoding="utf-8") as jsonfile:
    json.dump(articles_data, jsonfile, ensure_ascii=False, indent=4)

# Log summary information
logger.info(f"Data saved in {output_path}")
logger.info(f"Number of articles recorded: {len(articles_data)}")
logger.info(f"Number of 404 errors: {error_404_count}")
logger.info(f"Number of other errors: {other_error_count}")
logger.info(f"Number of articles with missing info: {missing_info_count}")
