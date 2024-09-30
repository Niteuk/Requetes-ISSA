import json
from collections import defaultdict


def analyze_sdgs_from_json(file_path):
    """
    The function `analyze_sdgs_from_json` processes JSON data to analyze Sustainable Development Goals
    (SDGs) occurrences and average scores, then saves the results in a JSON file.
    """
    # Dictionnaires pour compter les occurrences et sommer les scores
    sdg_count = defaultdict(int)
    sdg_scores = defaultdict(float)
    sdg_labels = {}

    # Charger les données du fichier JSON
    with open(file_path, "r", encoding="utf-8") as jsonfile:
        articles = json.load(jsonfile)

    # Parcourir chaque article pour extraire les SDGs
    for article in articles:
        if "SDGs" in article:
            seen_sdgs = set()  # Pour suivre les SDGs déjà comptés pour cet article
            for sdg in article["SDGs"]:
                sdg_id = sdg["ID"]
                sdg_name = sdg["Name"]
                sdg_score = (
                    sdg["Score"] if sdg["Score"] is not None else 0
                )  # Utiliser 0 si le score est None

                if sdg_id not in seen_sdgs:
                    sdg_count[sdg_id] += 1
                    sdg_scores[sdg_id] += sdg_score
                    sdg_labels[sdg_id] = sdg_name
                    seen_sdgs.add(sdg_id)  # Marquer ce SDG comme vu

    # Calculer la moyenne des scores pour chaque SDG
    sdg_average_scores = {
        sdg_id: (sdg_scores[sdg_id] / sdg_count[sdg_id]) for sdg_id in sdg_count
    }

    # Créer la liste des résultats
    results = []
    for sdg_id in sdg_count:
        results.append(
            {
                "sdg": sdg_id,
                "label": sdg_labels[sdg_id],
                "occurrences": sdg_count[sdg_id],
                "avg_score": sdg_average_scores[sdg_id],
            }
        )

    # Trier les résultats par nombre d'occurrences dans l'ordre décroissant
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

    # Écrire les résultats dans un fichier JSON
    output_path = "Data_Analysis/results/sdgs_count_result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print(f"Data saved in '{output_path}'.")


# Utiliser le chemin vers votre fichier JSON
analyze_sdgs_from_json("article_data.json")
