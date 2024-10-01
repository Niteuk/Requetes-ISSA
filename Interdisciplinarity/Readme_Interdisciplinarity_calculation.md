# Calcul de l'interdisciplinarité avec l'indice de Rao-Stirling

Ce dépôt explique et implémente l'indice de Rao-Stirling pour mesurer l'interdisciplinarité dans un ensemble d'articles scientifiques. L'indice combine à la fois la proportion des citations et la dissimilarité entre les sujets (topics) des articles cités.


## Étapes du calcul

### 1. Proportions des citations (p_i)
La première étape consiste à calculer la proportion d’apparition de chaque sujet parmi les articles cités via la fonction `create_citation_proportion_matrix()`. La proportion est définie comme :
p_i = nombre d'apparitions du sujet i / total des sujets cités


Par exemple, si un sujet T_1 apparaît 3 fois dans les articles cités, et que le total des sujets est de 10, alors :
p_1 = 3 / 10 = 0.3


### 2. Matrice de dissimilarité (d_ij)
La fonction `create_dissimilarity_matrix()` génère des combinaisons de deux sujets cités (T_i, T_j) et calcule leur dissimilarité en fonction de leur niveau hiérarchique : topics, subfields, fields, ou domains. La distance d_ij entre deux sujets est calculée ainsi :

- **Topics** (même sujet) : distance d = 0
- **Subfields** : distance d = 0.1
- **Fields** : distance d = 0.4
- **Domains** : distance d = 0.8
- **Max** (aucun lien commun) : distance d = 1

L'ensemble des dissimilarités est ensuite moyenné pour donner une **dissimilarité moyenne** (d̄) entre tous les sujets cités.


### 3. Calcul de l'indice de Rao-Stirling
L'indice de Rao-Stirling combine les proportions p_i et p_j des sujets cités et la dissimilarité d_ij entre eux. Il est calculé comme suit :
RS = ∑ p_i * p_j * d_ij

Dans le script, cette formule est implémentée dans `calculate_rao_stirling_index()`. Pour chaque paire de sujets i et j, le script multiplie la proportion p_i de chaque sujet par p_j et par la dissimilarité d_ij entre eux.

### Exemple de calcul :
- **Proportions** : Supposons que les proportions des sujets soient p_1 = 0.3, p_2 = 0.2, p_3 = 0.5.
- **Dissimilarités** : Les dissimilarités entre les sujets sont d_12 = 0.1, d_13 = 0.4, d_23 = 0.8.
- **Indice de Rao-Stirling** : RS = (0.3 * 0.2 * 0.1) + (0.3 * 0.5 * 0.4) + (0.2 * 0.5 * 0.8) = 0.006 + 0.06 + 0.08 = 0.146


### 4. Résultats et matrice de citation
Le script génère une matrice complète de citations en utilisant `create_full_citation_matrix()`, et sauvegarde les résultats de l'indice de Rao-Stirling dans un fichier JSON.


## Conclusion
Ce script permet de calculer un score d'interdisciplinarité pour chaque article en fonction des sujets abordés dans les articles cités. Cela permet de mesurer la diversité disciplinaire d'un ensemble de publications.




