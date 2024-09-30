import requests

# Liste des URLs pour les 17 SDGs
sdg_urls = [
    "https://metadata.un.org/sdg/1",
    "https://metadata.un.org/sdg/2",
    "https://metadata.un.org/sdg/3",
    "https://metadata.un.org/sdg/4",
    "https://metadata.un.org/sdg/5",
    "https://metadata.un.org/sdg/6",
    "https://metadata.un.org/sdg/7",
    "https://metadata.un.org/sdg/8",
    "https://metadata.un.org/sdg/9",
    "https://metadata.un.org/sdg/10",
    "https://metadata.un.org/sdg/11",
    "https://metadata.un.org/sdg/12",
    "https://metadata.un.org/sdg/13",
    "https://metadata.un.org/sdg/14",
    "https://metadata.un.org/sdg/15",
    "https://metadata.un.org/sdg/16",
    "https://metadata.un.org/sdg/17",
]

# Fichier de sortie RDF
output_file = "Object_Lists/results/sdgs_data.rdf"

# En-têtes pour accepter le format Turtle
headers = {"Accept": "text/turtle"}


# Fonction pour récupérer les données d'une URL et les écrire dans un fichier
def fetch_and_write_sdg_data(url, output_file):
    """
    The function fetches data from a list of URLs representing Sustainable Development Goals (SDGs) and
    writes the data to an output file, overwriting any existing content in the file.
    """
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    with open(output_file, "a", encoding="utf-8") as f:
        f.write(response.text)
        f.write("\n\n")


# Supprimer le contenu précédent du fichier de sortie, s'il existe
with open(output_file, "w", encoding="utf-8") as f:
    f.write("")

# Récupérer les données pour chaque SDG et les écrire dans le fichier de sortie
for url in sdg_urls:
    fetch_and_write_sdg_data(url, output_file)

print(f"Data for all SDGs saved in '{output_file}'.")
