## Data_Analysis

Ce dépôt contient plusieurs scripts Python qui analysent et visualisent des données liées aux Objectifs de Développement Durable (SDGs), aux topics, aux fields, aux subfields, et aux domains extraits de diverses sources. Les scripts permettent d'analyser les occurrences de ces entités dans des articles, de calculer les scores moyens et de générer des graphiques pour visualiser les résultats.

## Structure du dépôt

- count_Domains.py : Analyse les occurrences des "domains" et calcule les scores moyens à partir d'un fichier JSON.
- count_Fields.py : Analyse les occurrences des "fields" et calcule les scores moyens à partir d'un fichier JSON.
- count_SubFields.py : Analyse les occurrences des "subfields" et calcule les scores moyens à partir d'un fichier JSON.
- count_Topics.py : Analyse les occurrences des "topics" et calcule les scores moyens à partir d'un fichier JSON.
- count_Sdg.py : Analyse les occurrences des "SDGs" et calcule les scores moyens à partir d'un fichier JSON.
- countSDGtotal.py : Compte le nombre d'articles ayant au moins un SDG et le nombre d'articles sans SDG.
- create_Graph_Analysis.py : Génère des graphiques pour visualiser les occurrences et les scores moyens des différentes entités (SDGs, topics, fields, subfields, domains) à partir des fichiers JSON produits par les autres scripts.


## Scripts

1. count_Domains.py (et autres scripts d'analyse d'occurences)
- Description :
Ce script analyse les occurrences des "domains" et calcule les scores moyens associés dans un fichier JSON contenant les données des articles. Des scripts similaires existent pour les "fields", "subfields", "topics" et "Sdg" (count_Fields.py, count_SubFields.py, count_Topics.py, count_Sdg.py).

- Fonctionnalité :
Lit les données d'un fichier JSON spécifié (article_data.json).
Compte le nombre d'occurrences pour chaque domaine.
Calcule le score moyen associé à chaque domaine.
Sauvegarde les résultats dans un fichier JSON (Data_Analysis/results/domains_count_result.json).

- Utilisation :
Pour exécuter le script pour analyser les "domains" :

    ```bash
    python count_Domains.py
    ```

Le fichier de sortie contiendra les résultats dans Data_Analysis/results/domains_count_result.json.

Pour les autres scripts d'analyse, remplacez simplement count_Domains.py par count_Fields.py, count_SubFields.py, count_Topics.py ou count_Sdg.py.

2. countSDGtotal.py
- Description :
Ce script compte le nombre d'articles ayant au moins un SDG (Sustainable Development Goal) et le nombre d'articles sans SDG.

- Fonctionnalité :
Lit les données à partir d'un fichier JSON spécifié (article_data.json).
Compte les articles avec et sans SDGs.
Affiche le nombre d'articles dans chaque catégorie.

- Utilisation :
Pour exécuter le script :

    ```bash
    python countSDGtotal.py
    ```

Le résultat affichera le nombre d'articles avec et sans SDGs dans la console.

3. create_Graph_Analysis.py
- Description :
Ce script génère des graphiques pour visualiser les occurrences et les scores moyens des différentes entités (SDGs, topics, fields, subfields, domains) à partir des fichiers JSON produits par les autres scripts.

- Fonctionnalité :
Lit les données à partir des fichiers JSON générés par les autres scripts (sdgs_count_result.json, topics_count_result.json, etc.).
Trie les données par occurrences.
Génère des graphiques à barres horizontales affichant les occurrences et les scores moyens.
Sauvegarde les graphiques dans le répertoire Data_Analysis/Graph_Analysis/.

- Utilisation :
Pour exécuter le script et générer des graphiques pour les SDGs :

    ```bash
    python create_Graph_Analysis.py
    ```

Les fichiers de sortie contiendront les graphiques pour les entités spécifiées dans le répertoire Data_Analysis/Graph_Analysis/. Par exemple :
sdgs_all_occurrences_avg_scores.png
topics_top40_occurrences_avg_scores.png
domains_all_occurrences_avg_scores.png


## Conclusion

1. Détails des scripts d'analyse (count_Domains.py, count_Fields.py, count_SubFields.py, count_Topics.py) :
- analyze_domains_from_json(file_path) : Fonction principale qui lit les données JSON, analyse les domaines (ou autres entités), et sauvegarde les résultats triés dans un fichier JSON.
- output_file : Fichier où les résultats des occurrences et scores moyens sont stockés (par ex. domains_count_result.json).

2. Script countSDGtotal.py :
- count_articles_with_and_without_sdgs(file_path) : Fonction qui compte le nombre d'articles avec et sans SDGs.

3. Script create_Graph_Analysis.py :
- plot_data_from_json(file_path, entity_type, top_n, bottom_n) : Fonction principale qui génère des graphiques pour les entités spécifiées et les sauvegarde en fonction des occurrences et des scores moyens.
- plot_bar_chart(df, entity_type, suffix) : Génère un graphique à barres horizontales en fonction des données triées.