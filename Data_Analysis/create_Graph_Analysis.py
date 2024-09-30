import json
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.cm as cm


def plot_data_from_json(file_path, entity_type, top_n=None, bottom_n=None):
    """
    The function `plot_data_from_json` reads data from a JSON file, extracts labels, occurrences, and
    average scores, sorts the data by occurrences, and then plots a bar chart based on specified top and
    bottom values or displays all data if none are specified.
    """
    with open(file_path, "r", encoding="utf-8") as jsonfile:
        data = json.load(jsonfile)["results"]  # Extraire les résultats

    # Extraire les labels, les occurrences et les scores moyens
    labels = [item["label"] for item in data]
    occurrences = [item["occurrences"] for item in data]
    avg_scores = [item["avg_score"] for item in data]

    # Créer un DataFrame pour faciliter le tri
    df = pd.DataFrame(
        {"Label": labels, "Occurrences": occurrences, "AvgScore": avg_scores}
    )

    # Trier les données par Occurrences
    df = df.sort_values(by="Occurrences", ascending=False)

    if top_n:
        df_top = df.head(top_n)
        plot_bar_chart(df_top, entity_type, f"top{top_n}")

    if bottom_n:
        df_bottom = df.tail(bottom_n)
        plot_bar_chart(df_bottom, entity_type, f"bottom{bottom_n}")

    # Si ni top_n ni bottom_n n'est spécifié, on affiche tout
    if not top_n and not bottom_n:
        plot_bar_chart(df, entity_type, "all")


def plot_bar_chart(df, entity_type, suffix):
    """
    The function `plot_bar_chart` generates a horizontal bar chart displaying occurrences and average
    scores for a given entity type with a specified suffix.
    """
    # Normaliser les scores moyens pour le mappage des couleurs
    norm = plt.Normalize(df["AvgScore"].min(), df["AvgScore"].max())
    cmap = cm.get_cmap("viridis")

    # Générer le graphique à barres pour les occurrences
    plt.figure(figsize=(10, 8))
    bars = plt.barh(df["Label"], df["Occurrences"], color=cmap(norm(df["AvgScore"])))
    plt.xlabel("Occurrences")
    plt.ylabel("Label")
    plt.title(
        f"Occurrences and Average Scores of {entity_type.capitalize()} ({suffix})"
    )
    plt.gca().invert_yaxis()  # Inverser l'axe y pour afficher les labels dans l'ordre descendant

    # Ajouter les occurrences comme étiquettes sur les barres
    for bar, occurrences in zip(bars, df["Occurrences"]):
        plt.text(
            bar.get_width(),
            bar.get_y() + bar.get_height() / 2,
            f"{occurrences}",
            va="center",
        )

    # Ajouter une barre de couleur pour les scores moyens
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=plt.gca())
    cbar.set_label("Average Score")

    plt.tight_layout()
    plt.savefig(
        f"Data_Analysis/Graph_Analysis/{entity_type}_{suffix}_occurrences_avg_scores.png"
    )
    plt.close()

    print(
        f"Graph saved for {entity_type} ({suffix}) in 'Data_Analysis/Graph_Analysis/{entity_type}_{suffix}_occurrences_avg_scores.png'."
    )


# Créer des graphiques pour les SDGs (tous)
plot_data_from_json("Data_Analysis/sdgs_count_result.json", "sdgs")

# Créer des graphiques pour les Topics (top 40 et bottom 40)
plot_data_from_json(
    "Data_Analysis/topics_count_result.json", "topics", top_n=40, bottom_n=40
)

# Créer des graphiques pour les Fields (tous)
plot_data_from_json("Data_Analysis/fields_count_result.json", "fields")

# Créer des graphiques pour les Subfields (top 40 et bottom 40)
plot_data_from_json(
    "Data_Analysis/subfields_count_result.json", "subfields", top_n=40, bottom_n=40
)

# Créer des graphiques pour les Domains (tous)
plot_data_from_json("Data_Analysis/domains_count_result.json", "domains")
