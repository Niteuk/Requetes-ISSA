import os
import numpy as np
import json
import logging
import logging.config
import yaml
from collections import defaultdict
from itertools import combinations
import csv

# Configure logging from a YAML file
with open("config/logging.yaml", "rt") as f:
    config_log = yaml.safe_load(f.read())
    logging.config.dictConfig(config_log)
    logger = logging.getLogger(__name__)


# Load YAML configuration
def load_config(config_file):
    """
    Load the configuration from the given YAML file.
    """
    logger.debug(f"Loading configuration from {config_file}")
    with open(config_file, "r") as cfg:
        return yaml.safe_load(cfg)


# Dynamically append the level to file paths
def append_level_to_filepath(filepath, level):
    """
    Appends the level (topics, subfields, fields, domains) to the file path.
    """
    base, ext = os.path.splitext(filepath)
    return f"{base}_{level}{ext}"


# Load article data from a JSON file
def load_article_data(filepath):
    """
    Load article data from the given JSON file.
    """
    logger.debug(f"Loading article data from {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# Create citation proportions (p_ij) based on the frequency of topics in cited articles
def create_citation_proportion_matrix(article, level):
    """
    Calculate the proportion of topics based on their occurrence in cited articles at a specified level.
    """
    logging.debug(
        f"Calculating citation proportions for {article['DOI']} at level {level}"
    )
    levels = {
        "topics": "Name",
        "subfields": "Subfield",
        "fields": "Field",
        "domains": "Domain",
    }
    selected_level = levels[level]

    topic_count = defaultdict(int)
    total_topics = 0

    for cited_article in article["Cited_articles"]:
        for topic in cited_article["Topics"]:
            entity = (
                topic[selected_level]
                if level == "topics"
                else topic[selected_level]["Name"]
            )
            topic_count[entity] += 1
            total_topics += 1

    citation_proportion_matrix = {}

    if total_topics > 0:
        for topic, count in topic_count.items():
            citation_proportion_matrix[topic] = count / total_topics

    return citation_proportion_matrix, topic_count.keys()


# Create full citation matrix for all articles
def create_full_citation_matrix(articles, topics_list, level):
    """
    Generate a matrix containing citation proportions for articles across specified topics, including a column for DOI.
    """
    logging.info(f"Creating full citation matrix at level {level}")
    num_articles = len(articles)
    num_topics = len(topics_list)
    full_citation_matrix = np.zeros(
        (num_articles, num_topics + 1), dtype=object
    )  # Add 1 for the DOI column

    for i, article in enumerate(articles):
        full_citation_matrix[i, 0] = article["DOI"]  # First column for DOI
        citation_proportion_matrix, _ = create_citation_proportion_matrix(
            article, level
        )

        # Fill in the matrix
        for j, topic in enumerate(topics_list):
            if topic in citation_proportion_matrix:
                full_citation_matrix[i, j + 1] = citation_proportion_matrix[topic]
            else:
                full_citation_matrix[i, j + 1] = (
                    0  # If topic doesn't exist in the article
                )

    return full_citation_matrix


# Precompute the levels (hierarchical information) for entities
def precompute_entity_levels(articles, level):
    """
    Precompute entity levels based on the specified level (topics, subfields, fields, or domains) from a list of articles.
    """
    logging.debug(f"Precomputing entity levels for {level}")
    entity_levels = defaultdict(dict)
    levels = {
        "topics": "Name",
        "subfields": "Subfield",
        "fields": "Field",
        "domains": "Domain",
    }
    selected_level = levels[level]

    for article in articles:
        for topic in article["Topics"]:
            entity = (
                topic[selected_level]
                if level == "topics"
                else topic[selected_level]["Name"]
            )
            entity_levels[entity] = topic
        for cited_article in article["Cited_articles"]:
            for topic in cited_article["Topics"]:
                entity = (
                    topic[selected_level]
                    if level == "topics"
                    else topic[selected_level]["Name"]
                )
                entity_levels[entity] = topic
    return entity_levels


# Create dissimilarity matrix based on combinations of topics
def create_dissimilarity_matrix(cited_topics, entity_levels, level):
    """
    Calculate the average dissimilarity between pairs of topics based on their corresponding levels in a given dictionary.
    """
    logging.debug(f"Creating dissimilarity matrix for {level}")
    topic_pairs = list(combinations(cited_topics, 2))  # Generate unique topic pairs
    total_dissimilarity = 0
    num_pairs = len(topic_pairs)

    distances = {
        "topics": 0,
        "subfields": 0.125,
        "fields": 0.25,
        "domains": 0.5,
        "max": 1,
    }

    # Calculate the average distance for all pairs
    for topic_i, topic_j in topic_pairs:
        level_i = entity_levels.get(topic_i)
        level_j = entity_levels.get(topic_j)
        total_dissimilarity += calculate_distance(level_i, level_j, distances)

    if num_pairs > 0:
        avg_dissimilarity = total_dissimilarity / num_pairs
    else:
        avg_dissimilarity = 1
    return avg_dissimilarity


# Function to calculate the distance between two topics
def calculate_distance(level_i, level_j, distances):
    """
    Compare two levels based on their attributes and return a specific distance value.
    """
    if not level_i or not level_j:
        return distances["max"]
    if level_i["Name"] == level_j["Name"]:
        return distances["topics"]
    if (
        "Subfield" in level_i
        and "Subfield" in level_j
        and level_i["Subfield"]["Name"] == level_j["Subfield"]["Name"]
    ):
        return distances["subfields"]
    if (
        "Field" in level_i
        and "Field" in level_j
        and level_i["Field"]["Name"] == level_j["Field"]["Name"]
    ):
        return distances["fields"]
    if (
        "Domain" in level_i
        and "Domain" in level_j
        and level_i["Domain"]["Name"] == level_j["Domain"]["Name"]
    ):
        return distances["domains"]
    return distances["max"]


# Calculate the Rao-Stirling index
def calculate_rao_stirling_index(citation_proportion_matrix, avg_dissimilarity):
    """
    Calculate the Rao-Stirling index based on a citation proportion matrix and average dissimilarity.
    """
    logging.debug("Calculating Rao-Stirling index")
    rao_stirling_index = 0.0
    topics = list(citation_proportion_matrix.keys())

    for i, topic_i in enumerate(topics):
        for j, topic_j in enumerate(topics):
            if i != j:
                p_i = citation_proportion_matrix[topic_i]
                p_j = citation_proportion_matrix[topic_j]
                rao_stirling_index += p_i * p_j * avg_dissimilarity

    return rao_stirling_index


# Save results to a file
def save_results(results, filepath):
    """
    Save the results to a file in JSON format with specified encoding and indentation.
    """
    logging.info(f"Saving results to {filepath}")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


# Save the matrix with proper quoting of topics
def save_citation_matrix_with_topics(matrix, header_row, filepath):
    """
    Save a citation matrix with topics to a CSV file.
    """
    logger.info(f"Saving citation matrix to {filepath}")
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(header_row)
        writer.writerows(matrix)


# Main script function
def main(create_full_matrix=False):
    """Main function to calculate the Rao-Stirling index for articles and save the results to a file."""
    config = load_config("config/Interdisciplinarity/calcul_rao_stirling.yaml")

    level = config.get(
        "level", "topics"
    )  # Default to topics if not specified (can be topics, subfields, fields, or domains adjust in the config file)
    logging.info(f"Starting Rao-Stirling calculation at level: {level}")

    articles = load_article_data(config["data_file"])
    results = []
    missing_info_count = 0

    entity_levels = precompute_entity_levels(articles, level)

    if create_full_matrix:
        unique_topics = set()
        for article in articles:
            _, topics = create_citation_proportion_matrix(article, level)
            unique_topics.update(topics)
        unique_topics = list(unique_topics)
        header_row = ["DOI"] + unique_topics
        full_citation_matrix = create_full_citation_matrix(
            articles, unique_topics, level
        )

        # Adjust file names based on the selected level
        matrix_file = config["output_matrix_file"].replace("topics", level)
        if config.get("save_matrix", False):
            save_citation_matrix_with_topics(
                full_citation_matrix, header_row, matrix_file
            )

    for article in articles:
        if not article["Cited_articles"]:
            missing_info_count += 1
            logging.warning(f"No cited articles for {article['DOI']}")
            continue

        citation_proportion_matrix, cited_topics = create_citation_proportion_matrix(
            article, level
        )
        if not cited_topics:
            missing_info_count += 1
            logging.warning(f"No cited topics for {article['DOI']}")
            continue

        avg_dissimilarity = create_dissimilarity_matrix(
            cited_topics, entity_levels, level
        )
        rao_stirling_index = calculate_rao_stirling_index(
            citation_proportion_matrix, avg_dissimilarity
        )
        results.append(
            {
                "DOI": article["DOI"],
                "Title": article["Title"],
                "Rao Stirling Index": rao_stirling_index,
            }
        )

    result_file = config["output_result_file"].replace("topics", level)
    save_results(results, result_file)
    logging.info(f"Number of articles with missing info: {missing_info_count}")

    # Trigger Occurrence Calculation
    if config.get("run_occurrence_calculation", False):
        logging.info("Running occurrence calculation script")
        os.system("python Interdisciplinarity/calcul_occurences_rao_stirling.py")

    # Trigger RDF Conversion
    if config.get("run_rdf_conversion", False):
        logging.info("Running RDF conversion script")
        os.system("python Interdisciplinarity/rao_stirling_to_rdf.py")


if __name__ == "__main__":
    main(create_full_matrix=True)
