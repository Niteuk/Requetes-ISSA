## Data_Request

Ce dépôt contient des scripts Python permettant de récupérer des données à partir de l'API OpenAlex et d'un endpoint SPARQL, puis de sauvegarder ces données dans des fichiers RDF et JSON. Ces fichiers servent d'entrée pour d'autres dépôts tels que Data_Analysis et Interdisciplinarity.


## Structure du dépôt

- Request_OpenAlex_Json.py : Ce script récupère des informations sur les articles (DOI, titre, auteurs, SDGs, topics, etc.) à partir de l'API OpenAlex et les enregistre dans un fichier JSON. Ce fichier est utilisé pour les analyses dans Data_Analysis.
- Request_OpenAlex_Json_Interdisciplinarity.py : Semblable au script précédent, mais axé sur la récupération des articles et des informations interdisciplinaires pour le dépôt Interdisciplinarity.
- Request_OpenAlex_Authorships.py : Récupère des données sur les auteurs et les affiliations des articles et les enregistre dans un fichier RDF.
- Request_OpenAlex_Sdg.py : Récupère des données sur les Objectifs de Développement Durable (SDGs) associés aux articles et les enregistre dans un fichier RDF.
- Request_OpenAlex_Topics.py : Récupère des informations sur les topics des articles et les enregistre dans un fichier RDF.


## Scripts

1. Request_OpenAlex_Json.py
- Description :
Ce script interroge l'API OpenAlex pour récupérer des informations sur les articles scientifiques (DOI, titre, auteurs, affiliations, SDGs, topics, etc.) et les enregistre dans un fichier JSON pour une analyse ultérieure dans Data_Analysis.

- Fonctionnalité :
Récupère une liste de DOI depuis un endpoint SPARQL.
Pour chaque DOI, interroge l'API OpenAlex pour obtenir les informations des articles.
Extrait des informations telles que le titre, la date de publication, les auteurs, les affiliations, les SDGs, et les topics.
Sauvegarde les résultats dans un fichier JSON.

- Utilisation :
Pour exécuter le script :

    ```bash
    python Request_OpenAlex_Json.py
    ```

Le fichier de sortie sera sauvegardé dans output_paths/article_data (selon la configuration YAML dans le dossier de config).

2. Request_OpenAlex_Json_Interdisciplinarity.py
- Description :
Ce script récupère des informations interdisciplinaires sur les articles via l'API OpenAlex et un endpoint SPARQL, y compris les articles cités et les topics. Les résultats sont utilisés dans Interdisciplinarity.

- Fonctionnalité :
Récupère une liste de DOI à partir d'un endpoint SPARQL.
Pour chaque DOI, interroge l'API OpenAlex pour récupérer les articles ainsi que les articles cités.
Extrait les données pertinentes et les enregistre dans un fichier JSON.

- Utilisation :
Pour exécuter le script :

    ```bash
    python Request_OpenAlex_Json_Interdisciplinarity.py
    ```

Le fichier de sortie sera sauvegardé dans output_paths/article_data_interdisciplinarity.

3. Request_OpenAlex_Authorships.py
- Description :
Ce script interroge un microservice pour récupérer des informations sur les auteurs des articles et leurs affiliations, puis enregistre les résultats dans un fichier RDF.

- Fonctionnalité :
Récupère une liste de DOI et leurs URI depuis un endpoint SPARQL.
Pour chaque article, interroge un microservice pour obtenir les informations d'auteurs et d'affiliations.
Sauvegarde les résultats dans un fichier RDF.

- Utilisation :
Pour exécuter le script :

    ```bash
    python Request_OpenAlex_Authorships.py
    ```

Le fichier de sortie sera sauvegardé dans output_paths/authorship_data.

4. Request_OpenAlex_Sdg.py
- Description :
Ce script récupère des informations sur les Objectifs de Développement Durable (SDGs) associés aux articles scientifiques via un microservice et les enregistre dans un fichier RDF.

- Fonctionnalité :
Récupère une liste de DOI et leurs URI depuis un endpoint SPARQL.
Interroge un microservice pour obtenir des données sur les SDGs associés à chaque article.
Sauvegarde les résultats dans un fichier RDF.

- Utilisation :
Pour exécuter le script :

    ```bash
    python Request_OpenAlex_Sdg.py
    ```

Le fichier de sortie sera sauvegardé dans output_paths/sdg_data.

5. Request_OpenAlex_Topics.py
- Description :
Ce script récupère les informations sur les topics des articles scientifiques via un microservice, puis les enregistre dans un fichier RDF.

- Fonctionnalité :
Récupère une liste de DOI et leurs URI depuis un endpoint SPARQL.
Pour chaque article, interroge un microservice pour récupérer des informations sur les topics.
Sauvegarde les résultats dans un fichier RDF.

- Utilisation :
Pour exécuter le script :

    ```bash
    python Request_OpenAlex_Topics.py
    ```

Le fichier de sortie sera sauvegardé dans output_paths/topic_data.


## Conclusion

1. Détails des scripts pour les articles (Request_OpenAlex_Json.py, Request_OpenAlex_Json_Interdisciplinarity.py) :
- fetch_doi_list() : Fonction qui récupère la liste des DOI depuis un endpoint SPARQL.
- fetch_article_info(doi) : Fonction qui interroge l'API OpenAlex pour récupérer les informations sur un article scientifique.
- extract_article_data(article_info) : Fonction qui extrait les données pertinentes d'un article.
- process_doi(doi) : Fonction qui orchestre la récupération et l'extraction des données pour un DOI donné.

2. Détails des scripts pour les microservices (Request_OpenAlex_Authorships.py, Request_OpenAlex_Sdg.py, Request_OpenAlex_Topics.py) :
- fetch_doi_list() : Fonction qui récupère une liste de DOI et d'URI depuis un endpoint SPARQL.
- fetch_topic_data(document_uri, doi) : Fonction qui interroge un microservice pour récupérer des informations sur les topics, auteurs ou SDGs.
