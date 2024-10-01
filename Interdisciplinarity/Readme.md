## Interdisciplinarity

Ce dépôt contient des scripts Python qui permettent de calculer et d'analyser l'indice de Rao-Stirling basé sur les articles scientifiques et leurs citations, ainsi que de convertir les résultats en RDF pour une utilisation ultérieure. Ce dépôt se concentre sur l'analyse de l'interdisciplinarité dans les publications scientifiques.


## Structure du dépôt

- calcul_rao_stirling.py : Ce script calcule l'indice de Rao-Stirling pour une liste d'articles et génère une matrice de citation complète, ainsi que les dissimilarités entre les topics, subfields, fields, ou domains.
- calcul_occurences_rao_stirling.py : Ce script calcule la répartition des indices de Rao-Stirling dans des intervalles définis.
- rao_stirling_to_rdf.py : Ce script convertit les résultats des calculs de Rao-Stirling en RDF pour une meilleure interopérabilité avec des systèmes externes.
- Search_DOI_in_full_citation_matrix.py : Ce script permet de rechercher les topics non nuls associés à un DOI spécifique dans une matrice de citations.


## Scripts

1. calcul_rao_stirling.py
- Description :
Ce script calcule l'indice de Rao-Stirling pour une liste d'articles en se basant sur les citations et les dissimilarités entre les topics, subfields, fields, ou domains. Il permet également de créer une matrice de citation complète pour tous les articles.

- Fonctionnalité :
Calcule les proportions des topics cités pour chaque article.
Génère une matrice de citation complète.
Calcule l'indice de Rao-Stirling pour chaque article en fonction des topics cités et de leur dissimilarité.
Sauvegarde les résultats sous forme de fichier JSON et CSV.

- Utilisation :
Pour exécuter le script et générer la matrice de citation complète :

    ```bash
    python calcul_rao_stirling.py
    ```

Le fichier de sortie sera sauvegardé dans le chemin spécifié dans le fichier de configuration YAML (output_result_file).

2. calcul_occurences_rao_stirling.py
- Description :
Ce script calcule la répartition des indices de Rao-Stirling dans des intervalles définis et sauvegarde les résultats dans un fichier JSON.

- Fonctionnalité :
Charge les résultats des calculs de Rao-Stirling à partir d'un fichier JSON.
Calcule la fréquence des indices de Rao-Stirling dans des intervalles prédéfinis.
Sauvegarde les occurrences des indices dans un fichier JSON.

- Utilisation :
Pour exécuter le script :

    ```bash
    python calcul_occurences_rao_stirling.py
    ```

Le fichier de sortie sera sauvegardé dans le chemin spécifié dans le fichier de configuration YAML (output_filepath).

3. rao_stirling_to_rdf.py
- Description :
Ce script convertit les résultats des calculs de Rao-Stirling en RDF afin de permettre une meilleure interopérabilité des données avec d'autres systèmes. Il génère des annotations RDF à partir des résultats de Rao-Stirling et les associe aux articles.

- Fonctionnalité :
Charge les résultats des calculs de Rao-Stirling depuis un fichier JSON.
Génère des annotations RDF pour chaque article basé sur son DOI et son indice de Rao-Stirling.
Sauvegarde les résultats RDF.

- Utilisation :
Pour exécuter le script :

    ```bash
    python rao_stirling_to_rdf.py
    ```

Le fichier RDF sera sauvegardé dans le chemin spécifié dans le fichier de configuration YAML (output_filepath).

4. Search_DOI_in_full_citation_matrix.py
- Description :
Ce script permet de rechercher les topics associés à un DOI spécifique dans une matrice de citation, et d'afficher les topics ayant une valeur non nulle.

- Fonctionnalité :
Lit un fichier CSV contenant une matrice de citation.
Recherche les topics non nuls associés à un DOI spécifique.
Affiche les résultats dans la console.

- Utilisation :
Pour exécuter le script :

    ```bash
    python Search_DOI_in_full_citation_matrix.py
    ```

Vous pouvez remplacer le DOI et le chemin du fichier CSV par vos propres valeurs dans le script avant de l'exécuter.


## Conclusion

1. Détails du script calcul_rao_stirling.py :
- create_citation_proportion_matrix() : Calcule les proportions de citation pour chaque article en fonction des topics.
- calculate_rao_stirling_index() : Calcule l'indice de Rao-Stirling basé sur la dissimilarité moyenne des topics cités.
- create_full_citation_matrix() : Génère une matrice de citation pour tous les articles.

2. Script calcul_occurences_rao_stirling.py :
- calculate_occurrences() : Calcule la fréquence des indices de Rao-Stirling dans des intervalles spécifiés.

3. Script rao_stirling_to_rdf.py :
- convert_to_rdf() : Convertit les résultats des calculs de Rao-Stirling en annotations RDF.

4. Script Search_DOI_in_full_citation_matrix.py :
- get_non_zero_topics() : Recherche les topics ayant une valeur non nulle pour un DOI donné dans une matrice de citation.