import json
import hashlib
import logging
import logging.config
import yaml

# Configure logging from a YAML file
with open("config/logging.yaml", "rt") as f:
    config_log = yaml.safe_load(f.read())
    logging.config.dictConfig(config_log)
    logger = logging.getLogger(__name__)

# RDF Prefixes
PREFIXES = """
@prefix bibo:   <http://purl.org/ontology/bibo/> .
@prefix issa:   <http://data-issa.cirad.fr/> .
@prefix issapr: <http://data-issa.cirad.fr/property/> .
@prefix oa:     <http://www.w3.org/ns/oa#> .
@prefix rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .
"""


# Load YAML configuration
def load_config(config_file):
    """
    Load the configuration from the given YAML file.
    """
    logger.debug(f"Loading configuration from {config_file}")
    with open(config_file, "r") as cfg:
        return yaml.safe_load(cfg)


# Load JSON data
def load_json(filepath):
    """
    The function `load_json` reads and loads a JSON file from the specified filepath.
    """
    logger.debug(f"Loading JSON data from {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# Generate SHA-1 hash for unique identifier
def generate_sha1(document_uri, rao_index):
    """
    The function `generate_sha1` takes a document URI and an index, combines them, calculates the SHA-1
    hash, and returns the hexadecimal digest.
    """
    logger.debug(f"Generating SHA-1 for {document_uri} with index {rao_index}")
    sha1 = hashlib.sha1()
    sha1.update(f"{document_uri}{rao_index}".encode("utf-8"))
    return sha1.hexdigest()


# Determine the Rao-Stirling interval
def get_rao_stirling_interval(rao_index):
    """
    The function `get_rao_stirling_interval` categorizes a given RAO index into specific intervals.
    """
    logger.debug(f"Determining interval for Rao Stirling Index: {rao_index}")
    if 0.0 <= rao_index < 0.2:
        return "[0.0-0.2["
    elif 0.2 <= rao_index < 0.4:
        return "[0.2-0.4["
    elif 0.4 <= rao_index < 0.6:
        return "[0.4-0.6["
    elif 0.6 <= rao_index < 0.8:
        return "[0.6-0.8["
    elif 0.8 <= rao_index <= 1.0:
        return "[0.8-1.0]"
    return ""


# Convert JSON data to RDF format
def convert_to_rdf(data):
    """
    The function `convert_to_rdf` generates RDF data for each item in the input data, based on DOI and
    Rao Stirling Index values.
    """
    logger.debug("Converting JSON data to RDF format")
    rdf_data = []
    for item in data:
        sha1_hash = generate_sha1(item["DOI"], item["Rao Stirling Index"])
        annotation_uri = f"http://data-issa.cirad.fr/raoAnnotation/{sha1_hash}"
        rao_value = f"{item['Rao Stirling Index']:.3f}"
        interval = get_rao_stirling_interval(item["Rao Stirling Index"])

        rdf_data.append(
            f"""
<{annotation_uri}>
    a issa:RaoStirlingAnnotation ;
    oa:hasBody [
        rdf:value "{rao_value}"^^xsd:double ;
        issapr:raoStirlingDiscret "{interval}"
    ] ;
    oa:hasTarget <{item['DOI']}> .
"""
        )
    logger.info("RDF conversion completed")
    return "\n".join(rdf_data)


# Save RDF data to a file
def save_rdf(data, filepath):
    """
    The function `save_rdf` writes RDF data to a file specified by the `filepath` parameter.
    """
    logger.info(f"Saving RDF data to {filepath}")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(PREFIXES)
        f.write(data)
    logger.info(f"RDF data successfully saved to {filepath}")


# Main function
def main():
    """
    The main function loads JSON data, converts it to RDF format, and saves the RDF data to a file.
    """
    config = load_config("config/Interdisciplinarity/rao_stirling_in_rdf.yaml")
    try:
        logger.info("Starting RDF conversion process")
        json_data = load_json(config["input_filepath"])
        rdf_data = convert_to_rdf(json_data)
        save_rdf(rdf_data, config["output_filepath"])
        logger.info("RDF conversion process completed successfully")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
