import requests
import time
import logging
import logging.config
import yaml
from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, urlencode


# Load YAML configuration
def load_config(config_file):
    with open(config_file, "r") as cfg:
        return yaml.safe_load(cfg)


# Load configuration from file
config = load_config("config/Data_Request/requests.yaml")

# Configure logging from YAML
with open("config/logging.yaml", "rt") as f:
    config_log = yaml.safe_load(f.read())
    logging.config.dictConfig(config_log)
    logger = logging.getLogger(__name__)

# Use the config file parameters
MICROSERVICE_URL_TOPICS = config["MICROSERVICE"]["url_auth_topics"]
USE_MAILTO = config["API"]["use_mailto"]
PAUSE_DURATION = config["API"]["pause_duration"]
MAX_WORKERS = config["API"]["max_workers"]

# SPARQL prefixes
SPARQL_PREFIXES = """
PREFIX bibo: <http://purl.org/ontology/bibo/>
PREFIX issapr: <http://data-issa.cirad.fr/property/>
PREFIX oa: <http://www.w3.org/ns/oa#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX issa: <http://data-issa.cirad.fr/>
PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
"""


# Fetch DOI and document URIs from SPARQL endpoint
def fetch_doi_list():
    """Fetch DOI and document URIs from SPARQL endpoint"""
    logger.debug("Fetching DOI list from SPARQL endpoint")
    sparql = SPARQLWrapper(config["SPARQL"]["endpoint_url"])
    sparql.setQuery(config["SPARQL"]["query"])
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [
        (result["doi"]["value"], result["document"]["value"])
        for result in results["results"]["bindings"]
    ]


# Call the microservice for topic data
def fetch_topic_data(document_uri, doi):
    """Call the microservice for topic data"""
    try:
        encoded_document_uri = quote(document_uri, safe="")
        encoded_doi = quote(doi, safe="")
        sparql_query = SPARQL_PREFIXES + "CONSTRUCT WHERE { ?s ?p ?o. }"
        encoded_sparql_query = urlencode({"query": sparql_query})

        url = f"{MICROSERVICE_URL_TOPICS}?documentUri={encoded_document_uri}&documentDoi={encoded_doi}&{encoded_sparql_query}"
        headers = {"Accept": "text/turtle"}

        logger.debug(f"Fetching topic data for DOI {doi}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTPError: Could not add topic data for DOI {doi}: {e.response.text}"
        )
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"RequestException: Could not add topic data for DOI {doi}: {e}")
        return None


# Initialize lists and counters
rdf_results = []
error_count = 0

# Fetch DOI list and document URIs
doi_list = fetch_doi_list()
logger.info(f"Total DOIs retrieved: {len(doi_list)}")

# Multithreading with ThreadPoolExecutor
if USE_MAILTO:
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_doi = {
            executor.submit(fetch_topic_data, doc_uri, doi): (doc_uri, doi)
            for doi, doc_uri in doi_list
        }
        for future in tqdm(as_completed(future_to_doi), total=len(doi_list)):
            doc_uri, doi = future_to_doi[future]
            try:
                rdf_data = future.result()
                if rdf_data:
                    rdf_results.append(rdf_data)
                    logger.debug(f"Topic data for DOI {doi} recorded.")
                else:
                    error_count += 1
            except Exception as exc:
                logger.error(f"DOI {doi} generated an exception: {exc}")
                error_count += 1
else:
    for doi, doc_uri in tqdm(doi_list):
        try:
            rdf_data = fetch_topic_data(doc_uri, doi)
            if rdf_data:
                rdf_results.append(rdf_data)
                logger.debug(f"Topic data for DOI {doi} recorded.")
            else:
                error_count += 1
        except Exception as exc:
            logger.error(f"DOI {doi} generated an exception: {exc}")
            error_count += 1
        time.sleep(PAUSE_DURATION)

# Save RDF results to a Turtle file
output_path = config["output_paths"]["topic_data"]
with open(output_path, "w", encoding="utf-8") as rdf_file:
    rdf_file.write(SPARQL_PREFIXES)
    for rdf_data in rdf_results:
        for line in rdf_data.splitlines():
            if not line.startswith("@prefix"):
                rdf_file.write(line + "\n")

logger.info(f"Topic data saved in {output_path}")
logger.info(f"Number of successful records: {len(rdf_results)}")
logger.info(f"Number of errors: {error_count}")
