import json


def count_articles_with_and_without_sdgs(file_path):
    """
    The function counts the number of articles with at least one Sustainable Development Goal (SDG) and
    the number of articles without any SDGs.
    """
    with open(file_path, "r", encoding="utf-8") as jsonfile:
        articles = json.load(jsonfile)

    articles_with_sdgs = 0
    articles_without_sdgs = 0

    for article in articles:
        if "SDGs" in article and article["SDGs"]:
            articles_with_sdgs += 1
        else:
            articles_without_sdgs += 1

    print(f"Number of articles with at least one SDG: {articles_with_sdgs}")
    print(f"Number of articles without any SDGs: {articles_without_sdgs}")


# Utiliser le chemin vers votre fichier JSON
count_articles_with_and_without_sdgs("article_data.json")
