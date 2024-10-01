# Projet d'Analyse d'Interdisciplinarité et de données bibliométrique

Ce projet permet de calculer et d'analyser l'indice d'interdisciplinarité de publications scientifiques à l'aide de l'indice de Rao-Stirling. Il inclut plusieurs modules pour récupérer, traiter et analyser des données provenant de différentes API comme OpenAlex, ainsi que pour convertir les résultats en formats RDF pour des applications plus larges.


## Structure du Projet
Le projet est organisé en plusieurs répertoires principaux, chacun contenant des scripts spécifiques à une fonctionnalité :

- Data_Request : Contient les scripts pour récupérer les données depuis l'API OpenAlex et les convertir en fichiers JSON pour les analyses futures. Ce répertoire utilise des fichiers de configuration spécifiques situés dans le dossier config/Data_Request.

- Data_Analysis : Contient des scripts pour analyser les résultats obtenus (topics, fields, domains, SDGs) et générer des graphiques de visualisation.

- Interdisciplinarity : Contient les scripts pour calculer l'indice de Rao-Stirling et effectuer des calculs connexes. Ce répertoire utilise plusieurs fichiers de configuration situés dans le dossier config/Interdisciplinarity.

- Object_Lists : Contient des scripts pour récupérer et gérer des listes d'objets (SDGs, topics, fields, subfields) nécessaires pour l'analyse.


## Fonctionnalités
Calcul de l'indice de Rao-Stirling :

Mesure l'interdisciplinarité à travers les citations et les dissimilarités entre sujets dans les articles scientifiques.
Génération de matrices complètes de citation.
Analyse des Topics et SDGs :

Récupère et analyse des objets comme les Sustainable Development Goals (SDGs), et les topics des publications.
Génère des rapports sous forme de fichiers JSON et des graphiques pour visualiser les résultats.
Export en RDF :

Convertit les résultats d'analyse en format RDF pour une intégration dans des systèmes de gestion de données.


## Environnement et Dépendances

Le projet utilise Python 3.8+ et plusieurs bibliothèques, dont :

requests : Pour effectuer des requêtes HTTP vers les API.
numpy : Pour les calculs matriciels.
pandas : Pour la manipulation de données.
matplotlib : Pour la génération de graphiques.
SPARQLWrapper : Pour interagir avec les endpoints SPARQL.
PyYAML : Pour la gestion des fichiers de configuration YAML.
tqdm : Pour afficher des barres de progression lors de l'exécution de scripts longs.
concurrent.futures : Pour l'exécution parallèle des requêtes.


## Configuration et Logging

Le dossier config contient les fichiers de configuration nécessaires pour les différents répertoires du projet. Il est structuré comme suit :

- logging.yaml : Ce fichier configure le système de logging pour tous les scripts du projet. Il permet de suivre les différentes étapes d'exécution, de détecter les erreurs, et d'enregistrer des informations utiles pour le débogage. Tous les scripts dans les répertoires Data_Request et Interdisciplinarity utilisent ce fichier pour gérer leurs logs.

- Data_Request : Ce sous-dossier contient un fichier de configuration YAML utilisé par les scripts dans le répertoire Data_Request. Il définit :
Les endpoints SPARQL.
Les chemins de sortie des fichiers JSON et RDF.
Les paramètres pour l'API OpenAlex, tels que l'option mailto pour éviter les limitations d'API.

- Interdisciplinarity : Ce sous-dossier contient trois fichiers de configuration pour les différents calculs effectués dans le répertoire 
calcul_rao_stirling.yaml : Définit les paramètres pour le calcul de l'indice de Rao-Stirling, tels que le niveau de hiérarchie (topics, fields, domains).
calcul_occurences.yaml : Contient les paramètres pour le calcul des occurrences des résultats d'indice Rao-Stirling.
rao_stirling_in_rdf.yaml : Définit les paramètres pour la conversion des résultats en format RDF.

### Utilisation du Logging
Les répertoires Data_Request et Interdisciplinarity utilisent le fichier logging.yaml pour gérer l'enregistrement des événements, des erreurs, et des avertissements lors de l'exécution des scripts. Les niveaux de logging (DEBUG, INFO, WARNING, ERROR) peuvent être ajustés dans ce fichier pour augmenter ou réduire le niveau de détail des logs.


## Conclusion
Ce projet dans le cadre du projet ISSA fournit un cadre complet pour mesurer l'interdisciplinarité des publications scientifiques à l'aide de l'indice de Rao-Stirling. Il permet de récupérer, analyser, et visualiser des données à partir de sources ouvertes comme OpenAlex et de les convertir en formats RDF pour une intégration plus large.