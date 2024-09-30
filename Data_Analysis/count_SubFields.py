import json
from collections import defaultdict


def analyze_subfields_from_json(file_path):
    """
    The function `analyze_subfields_from_json` reads JSON data, analyzes subfields within articles,
    calculates average scores, and saves the results in a JSON file.
    """
    subfield_count = defaultdict(int)
    subfield_scores = defaultdict(float)
    subfield_labels = {}

    with open(file_path, "r", encoding="utf-8") as jsonfile:
        articles = json.load(jsonfile)

    for article in articles:
        if "Topics" in article:
            seen_subfields = (
                set()
            )  # Pour suivre les sous-champs déjà comptés pour cet article
            for topic in article["Topics"]:
                subfield = topic["Subfield"]
                if subfield:
                    subfield_id = subfield["ID"]
                    subfield_name = subfield["Name"]
                    subfield_score = topic["Score"] if topic["Score"] is not None else 0

                    if subfield_id not in seen_subfields:
                        subfield_count[subfield_id] += 1
                        subfield_scores[subfield_id] += subfield_score
                        subfield_labels[subfield_id] = subfield_name
                        seen_subfields.add(subfield_id)

    subfield_average_scores = {
        subfield_id: (subfield_scores[subfield_id] / subfield_count[subfield_id])
        for subfield_id in subfield_count
    }

    results = []
    for subfield_id in subfield_count:
        results.append(
            {
                "subfield": subfield_id,
                "label": subfield_labels[subfield_id],
                "occurrences": subfield_count[subfield_id],
                "avg_score": subfield_average_scores[subfield_id],
            }
        )

    results_sorted = sorted(results, key=lambda x: x["occurrences"], reverse=True)

    # Ajouter la section "meta"
    output_data = {
        "meta": {
            "count": len(results_sorted),
            "db_response_time_ms": 5,
            "page": 1,
            "per_page": 100,
            "groups_count": None,
        },
        "results": results_sorted,
    }

    output_path = "Data_Analysis/results/subfields_count_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"Data saved in '{output_path}'.")


analyze_subfields_from_json("article_data.json")
