import requests
import json


def fetch_all_items(item_type):
    """
    The function `fetch_all_items` retrieves all items of a specified type from an API by paginating
    through the results.

    Returns:
      The function `fetch_all_items` returns a tuple containing two elements:
    1. `all_items`: a list of dictionaries, where each dictionary represents an item with keys "id" and
    "display_name".
    2. `meta_info`: a dictionary containing metadata information about the fetched items, such as total
    count, page number, etc.
    """
    base_url = f"https://api.openalex.org/{item_type}"
    params = {"per_page": 100, "page": 1}  # Nombre de résultats par page

    all_items = []
    meta_info = None
    while True:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Extraire l'ID et le display name pour chaque item
        for item in data["results"]:
            all_items.append({"id": item["id"], "display_name": item["display_name"]})

        # Afficher le statut de récupération des pages
        print(f"Fetched page {params['page']} with {len(data['results'])} {item_type}.")

        # Vérifier s'il y a une page suivante
        if len(data["results"]) < params["per_page"]:
            meta_info = data["meta"]
            break
        else:
            params["page"] += 1

    return all_items, meta_info


def save_to_json(data, meta_info, filename):
    """
    The function `save_to_json` saves data along with metadata to a JSON file with specified filename.
    """
    output = {
        "meta": {
            "count": meta_info["count"],
            "db_response_time_ms": meta_info["db_response_time_ms"],
            "page": meta_info["page"],
            "per_page": meta_info["per_page"],
            "groups_count": meta_info["groups_count"],
        },
        "results": data,
        "group_by": [],
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print(f"Data saved in '{filename}'.")


# Fonction pour récupérer, trier et sauvegarder les données pour un type donné
def process_and_save(item_type, filename):
    """
    The function `process_and_save` fetches items of a specified type, sorts them based on their ID, and
    saves them to a JSON file along with metadata.
    """
    items, meta_info = fetch_all_items(item_type)

    # Tri des items par l'ID, extraction de la partie numérique si elle existe
    if item_type == "sdgs":
        items_sorted = sorted(items, key=lambda x: int(x["id"].split("/")[-1]))
    else:
        items_sorted = sorted(items, key=lambda x: x["id"])

    save_to_json(items_sorted, meta_info, filename)


# Récupérer et sauvegarder les topics
process_and_save("topics", "Object_Lists/results/openalex_topics_list.json")

# Récupérer et sauvegarder les fields
process_and_save("fields", "Object_Lists/results/openalex_fields_list.json")

# Récupérer et sauvegarder les subfields
process_and_save("subfields", "Object_Lists/results/openalex_subfields_list.json")

# Récupérer et sauvegarder les domains
process_and_save("domains", "Object_Lists/results/openalex_domains_list.json")

# Récupérer et sauvegarder les sdgs
process_and_save("sdgs", "Object_Lists/results/openalex_sdgs_list.json")
