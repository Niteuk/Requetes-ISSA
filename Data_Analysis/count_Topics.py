import json
from collections import defaultdict


def analyze_topics_from_json(file_path):
    """
    The function `analyze_topics_from_json` reads JSON data, analyzes topic occurrences and scores, and
    saves the results in a JSON file.
    """
    topic_count = defaultdict(int)
    topic_scores = defaultdict(float)
    topic_labels = {}

    with open(file_path, "r", encoding="utf-8") as jsonfile:
        articles = json.load(jsonfile)

    for article in articles:
        if "Topics" in article:
            seen_topics = set()  # Pour suivre les sujets déjà comptés pour cet article
            for topic in article["Topics"]:
                topic_id = topic["ID"]
                topic_name = topic["Name"]
                topic_score = topic["Score"] if topic["Score"] is not None else 0

                if topic_id not in seen_topics:
                    topic_count[topic_id] += 1
                    topic_scores[topic_id] += topic_score
                    topic_labels[topic_id] = topic_name
                    seen_topics.add(topic_id)  # Marquer ce sujet comme vu

    topic_average_scores = {
        topic_id: (topic_scores[topic_id] / topic_count[topic_id])
        for topic_id in topic_count
    }

    results = []
    for topic_id in topic_count:
        results.append(
            {
                "topic": topic_id,
                "label": topic_labels[topic_id],
                "occurrences": topic_count[topic_id],
                "avg_score": topic_average_scores[topic_id],
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

    output_path = "Data_Analysis/results/topics_count_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"Data saved in '{output_path}'.")


# Utiliser le chemin vers votre fichier JSON
analyze_topics_from_json("article_data.json")
