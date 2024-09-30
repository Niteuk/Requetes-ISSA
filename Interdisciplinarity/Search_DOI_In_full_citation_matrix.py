import csv


def get_non_zero_topics(doi, filepath):
    """
    The function `get_non_zero_topics` reads a CSV file to find non-zero topics associated with a given
    DOI.

    Returns:
      The function `get_non_zero_topics` returns either a dictionary containing non-zero topics and
    their corresponding values for the provided DOI, or a message indicating that no non-zero topics
    were found for the DOI, or a message indicating that the provided DOI was not found in the file.
    """
    with open(filepath, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)

        # Get the header (first row) which contains the topics names
        header = next(reader)

        # Find the row corresponding to the provided DOI
        for row in reader:
            if row[0] == doi:  # First column contains DOI
                non_zero_topics = {}

                # Iterate through the row and find non-zero values
                for index, value in enumerate(row[1:], start=1):  # Skip DOI column
                    if float(value) != 0:
                        non_zero_topics[header[index]] = float(value)

                if non_zero_topics:
                    return non_zero_topics
                else:
                    return "No non-zero topics found for this DOI."

        return "DOI not found in the file."


# Example usage
doi_input = "https://doi.org/10.4000/etudesafricaines.28"
csv_filepath = (
    "Interdisciplinarity/results/rao_stirling_upgrade_full_citation_matrix.csv"
)
result = get_non_zero_topics(doi_input, csv_filepath)

print(result)
