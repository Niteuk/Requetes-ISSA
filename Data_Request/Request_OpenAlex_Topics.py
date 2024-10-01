import logging
import logging.config
import requests
import time
import yaml
from SPARQLWrapper import SPARQLWrapper, JSON
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote, urlencode


def load_config(config_file):
    with open(config_file, "r") as cfg:
        return yaml.safe_load(cfg)


# Load configuration
config = load_config("config/Data_Request/requests.yaml")

# Configure logging
with open("config/logging.yaml", "rt") as f:
    config_log = yaml.safe_load(f.read())
    logging.config.dictConfig(config_log)
    logger = logging.getLogger(__name__)

# SPARQL prefixes
SPARQL_PREFIXES = """
PREFIX bibo:   <http://purl.org/ontology/bibo/>
PREFIX issapr: <http://data-issa.cirad.fr/property/>
PREFIX issa:   <http://data-issa.cirad.fr/>
PREFIX oa:     <http://www.w3.org/ns/oa#>
PREFIX rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd:    <http://www.w3.org/2001/XMLSchema#>
"""


def fetch_doi_list():
    """
    Fetch DOI list from SPARQL endpoint
    Returns:
        dict: dictionary with DOI as key and document URI as value
    """
    logger.debug("Fetching DOI list from SPARQL endpoint")
    sparql = SPARQLWrapper(config["issa_sparql_endpoint"]["endpoint_url"])
    sparql.setQuery(config["issa_sparql_endpoint"]["query"])
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return [
        (result["doi"]["value"], result["document"]["value"])
        for result in results["results"]["bindings"]
    ]


def fetch_data(document_uri, doi):
    """
    Fetch topics data for a given DOI and document URI
    from the SPARQL microservice

    Args:
        document_uri (str): document URI
        doi (str): document DOI

    Returns:
       str: RDF data in Turtle format
    """
    try:
        encoded_document_uri = quote(document_uri, safe="")
        encoded_doi = quote(doi, safe="")
        sparql_query = SPARQL_PREFIXES + "CONSTRUCT WHERE { ?s ?p ?o. }"
        encoded_sparql_query = urlencode({"query": sparql_query})

        url = f"{config['services']['topics']}?documentUri={encoded_document_uri}&documentDoi={encoded_doi}&{encoded_sparql_query}"
        headers = {"Accept": "text/turtle"}

        logger.debug(f"Fetching topic data for DOI {doi}")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"Could not get topic data for DOI {doi}: {e.response.text}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Could not get topic data for DOI {doi}: {e}")
        return None


if __name__ == "__main__":

    # Initialize lists and counters
    rdf_results = []
    error_count = 0

    # Fetch DOI list and document URIs
    doi_list = fetch_doi_list()
    logger.info(f"Total DOIs retrieved: {len(doi_list)}")

    if config["openalex_api"]["use_mailto"]:
        # Parallel execution with ThreadPoolExecutor
        with ThreadPoolExecutor(
            max_workers=config["openalex_api"]["max_workers"]
        ) as executor:
            future_to_doi = {
                executor.submit(fetch_data, doc_uri, doi): (doc_uri, doi)
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
                    logger.error(f"Exception while processing DOI {doi} : {exc}")
                    error_count += 1
    else:
        # Sequential execution
        for doi, doc_uri in tqdm(doi_list):
            try:
                rdf_data = fetch_data(doc_uri, doi)
                if rdf_data:
                    rdf_results.append(rdf_data)
                    logger.debug(f"Topic data for DOI {doi} recorded.")
                else:
                    error_count += 1
            except Exception as exc:
                logger.error(f"Exception while processing DOI {doi} : {exc}")
                error_count += 1
            time.sleep(config["openalex_api"]["pause_duration"])

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
