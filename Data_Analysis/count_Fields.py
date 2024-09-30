import json
from collections import defaultdict


def analyze_fields_from_json(file_path):
    """
    The function `analyze_fields_from_json` reads JSON data, analyzes field occurrences and scores, and
    saves the results in a JSON file.
    """
    field_count = defaultdict(int)
    field_scores = defaultdict(float)
    field_labels = {}

    with open(file_path, "r", encoding="utf-8") as jsonfile:
        articles = json.load(jsonfile)

    for article in articles:
        if "Topics" in article:
            seen_fields = set()  # Pour suivre les champs déjà comptés pour cet article
            for topic in article["Topics"]:
                field = topic["Field"]
                if field:
                    field_id = field["ID"]
                    field_name = field["Name"]
                    field_score = topic["Score"] if topic["Score"] is not None else 0

                    if field_id not in seen_fields:
                        field_count[field_id] += 1
                        field_scores[field_id] += field_score
                        field_labels[field_id] = field_name
                        seen_fields.add(field_id)  # Marquer ce champ comme vu

    field_average_scores = {
        field_id: (field_scores[field_id] / field_count[field_id])
        for field_id in field_count
    }

    results = []
    for field_id in field_count:
        results.append(
            {
                "field": field_id,
                "label": field_labels[field_id],
                "occurrences": field_count[field_id],
                "avg_score": field_average_scores[field_id],
            }
        )

    results_sorted = sorted(results, key=lambda x: x["occurrences"], reverse=True)

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

    output_path = "Data_Analysis/results/fields_count_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"Data saved in '{output_path}'.")


analyze_fields_from_json("article_data.json")
