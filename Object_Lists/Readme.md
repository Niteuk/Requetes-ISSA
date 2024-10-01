## Object_Lists

Ce dépôt contient deux scripts Python qui récupèrent des données sur les Objectifs de Développement Durable (SDGs) et d'autres objets à partir de diverses API, et qui les sauvegardent dans des fichiers au format RDF et JSON.


## Structure du dépôt

- Fetch_sdg_rdf.py : Ce script télécharge les données RDF des Objectifs de Développement Durable (SDGs) à partir des URLs spécifiques.
- Request_all_Objects.py : Ce script interroge l'API OpenAlex pour récupérer plusieurs types d'objets (topics, fields, subfields, domains, et sdgs), les trie, puis les sauvegarde dans des fichiers JSON.


## Scripts

1. Fetch_sdg_rdf.py
- Description :
Ce script récupère les données RDF des 17 Objectifs de Développement Durable (SDGs) en accédant aux URLs officielles, et les stocke dans un fichier .rdf.

- Fonctionnalité :
Accède à une liste de 17 URLs représentant chaque SDG.
Télécharge les données RDF.
Sauvegarde les résultats dans le fichier Object_Lists/results/sdgs_data.rdf.

- Utilisation :
Pour exécuter le script :   

    ```bash
    python Fetch_sdg_rdf.py
    ```

Le fichier de sortie contiendra les données RDF de tous les SDGs dans Object_Lists/results/sdgs_data.rdf.

2. Request_all_Objects.py
- Description :
Ce script interroge l'API OpenAlex pour récupérer plusieurs types d'objets : topics, fields, subfields, domains, et sdgs. Les données récupérées sont ensuite triées et sauvegardées dans des fichiers JSON.

- Fonctionnalité :
Pour chaque type d'objet (par exemple, topics, fields), le script :
Télécharge tous les éléments disponibles en paginant à travers l'API.
Trie les éléments récupérés.
Sauvegarde les données triées ainsi que les métadonnées associées dans un fichier JSON.

- Utilisation :
Pour exécuter le script :

    ```bash
    python Request_all_Objects.py
    ```

Les fichiers de sortie seront sauvegardés dans le dossier Object_Lists/results/ sous les noms suivants :
openalex_topics_list.json
openalex_fields_list.json
openalex_subfields_list.json
openalex_domains_list.json
openalex_sdgs_list.json


## Conclusion

1. Détails du script Fetch_sdg_rdf.py :
- sdg_urls : Liste des URLs officielles pour chaque SDG.
- fetch_and_write_sdg_data(url, output_file) : Fonction qui récupère les données RDF depuis une URL et les écrit dans un fichier.
- output_file : Fichier où les données RDF sont stockées.

2. Fichier Request_all_Objects.py :
- fetch_all_items(item_type) : Fonction qui interroge l'API OpenAlex pour récupérer tous les éléments d'un type donné (par ex. topics, fields).
- save_to_json(data, meta_info, filename) : Fonction qui sauvegarde les données récupérées et les métadonnées dans un fichier JSON.
- process_and_save(item_type, filename) : Fonction principale qui gère la récupération, le tri et la sauvegarde des données pour un type donné.
