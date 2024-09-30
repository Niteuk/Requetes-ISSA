import json
import logging
import logging.config
import yaml

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


# Load JSON results
def load_results(filepath):
    """
    Load results from a JSON file.
    """
    logger.debug(f"Loading results from {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# Calculate occurrences of Rao-Stirling Index results
def calculate_occurrences(results, interval=0.1):
    """
    Calculate occurrences of results in specified intervals, keeping only the closed [0.9-1.0] interval.
    """
    logger.debug(f"Calculating occurrences with interval {interval}")
    occurrences = {}

    # Loop through the ranges, but exclude the interval [0.9-1.0[
    for i in range(0, int(1 / interval) - 1):  # Exclude the last interval
        lower_bound = round(i * interval, 1)
        upper_bound = round((i + 1) * interval, 1)
        occurrences[f"[{lower_bound}-{upper_bound}["] = 0

    # Add the closed interval [0.9-1.0]
    occurrences["[0.9-1.0]"] = 0

    for result in results:
        rao_index = result["Rao Stirling Index"]
        if 0.9 <= rao_index <= 1.0:
            occurrences["[0.9-1.0]"] += 1
        else:
            for i in range(0, int(1 / interval) - 1):
                lower_bound = round(i * interval, 1)
                upper_bound = round((i + 1) * interval, 1)
                if lower_bound <= rao_index < upper_bound:
                    occurrences[f"[{lower_bound}-{upper_bound}["] += 1
                    break

    logger.info("Occurrences calculated successfully")
    return occurrences


# Save occurrences to JSON file
def save_occurrences(occurrences, filepath):
    """
    Save occurrences to a JSON file.
    """
    logger.debug(f"Saving occurrences to {filepath}")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(occurrences, f, ensure_ascii=False, indent=4)
    logger.info(f"Occurrences saved in {filepath}")


# Main script function
def main():
    """
    Main function to load results, calculate occurrences, and save them to a file.
    """
    config = load_config("config/Interdisciplinarity/calcul_occurences.yaml")

    logger.info("Starting occurrence calculation")
    try:
        input_filepath = config["input_filepath"]
        output_filepath = config["output_filepath"]
        interval = config.get("interval", 0.1)

        results = load_results(input_filepath)
        occurrences = calculate_occurrences(results, interval)
        save_occurrences(occurrences, output_filepath)

        logger.info("Process completed successfully")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
