import json
from collections import defaultdict


def analyze_domains_from_json(file_path):
    """
    The function `analyze_domains_from_json` reads JSON data, analyzes domain information, calculates
    average scores, and saves the results in a JSON file.
    """
    domain_count = defaultdict(int)
    domain_scores = defaultdict(float)
    domain_labels = {}

    with open(file_path, "r", encoding="utf-8") as jsonfile:
        articles = json.load(jsonfile)

    for article in articles:
        if "Topics" in article:
            seen_domains = (
                set()
            )  # Pour suivre les domaines déjà comptés pour cet article
            for topic in article["Topics"]:
                domain = topic["Domain"]
                if domain:
                    domain_id = domain["ID"]
                    domain_name = domain["Name"]
                    domain_score = topic["Score"] if topic["Score"] is not None else 0

                    if domain_id not in seen_domains:
                        domain_count[domain_id] += 1
                        domain_scores[domain_id] += domain_score
                        domain_labels[domain_id] = domain_name
                        seen_domains.add(domain_id)  # Marquer ce domaine comme vu

    domain_average_scores = {
        domain_id: (domain_scores[domain_id] / domain_count[domain_id])
        for domain_id in domain_count
    }

    results = []
    for domain_id in domain_count:
        results.append(
            {
                "domain": domain_id,
                "label": domain_labels[domain_id],
                "occurrences": domain_count[domain_id],
                "avg_score": domain_average_scores[domain_id],
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

    output_path = "Data_Analysis/results/domains_count_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"Data saved in '{output_path}'.")


analyze_domains_from_json("article_data.json")
