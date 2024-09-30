Explicaitons Rao-Stirling_Upgrade:

Nous allons toujours calculer rao stirling à l'aide des citations et de la dissimilarité entre les topics.
Pour ce qui est de pij qui concerne les citations nous allons maintenant pour l'article évalué regarder seulement tous les topics des articles cités. Et nous allons attribuer la proportion d'apparition des ces topics dans les articles cités. Par exemple on évalue l'article A qui cites 3 articles. Au total ces 3 articles sont représentés par 10 topics. Ainsi on va assigner un pourcentage d'apparition de ces 10 topics parmis les 3 articles. Si les topics sont tous représentés 1 seule fois alors ils auront un score de 0.10 soit 10% (par exemple). Ensuite on fait ca pour tous les articles. 
Pour ce qui concerne la dissimilarité on va calculer la distance de chaque topics récupérer précedement dans les articles cités de l'article qu'on évalue puis on liste ces topics sous forme de combinaison de 2 sans remise pour ne pas avoir de répétition et on calcule leurs distance de la même manière qu'on faisait c'est à dire en assignant des poids de cette manière:
'topics': 0,
        'subfields': 0.1,
        'fields': 0.4,
        'domains': 0.8,
        'max': 1.

Pour chaque combinaison on obtient donc un score entre 0 et 1. Puis on additione chacune des scores des combinaisons et on divise par le nombre de combinaisons réalisés. Ce qui la aussi nous donne un score entre 0 et 1 et avec le score des citations et de la dissimilarité on peut faire rao stirling et obtenir la aussi un score entre 0 et 1








# Calcul de l'interdisciplinarité avec l'indice de Rao-Stirling


Le script utilise la **formule de Rao-Stirling** pour calculer l'interdisciplinarité. Cette formule prend en compte à la fois la **proportion** des citations et la **dissimilarité** entre les sujets (topics) des articles cités. Voici une explication détaillée de chaque étape :

### 1. **Proportions des citations (\( p_i \))**

Le script calcule la proportion d’apparition de chaque sujet parmi les articles cités via la fonction `create_citation_proportion_matrix()`. La proportion est définie comme :

\[
p_i = \frac{\text{nombre d'apparitions du sujet i}}{\text{total des sujets cités}}
\]

Exemple : Si un sujet \( T_1 \) apparaît 3 fois dans les articles cités, et que le total des sujets est 10, alors \( p_1 = 3/10 = 0.3 \).

### 2. **Matrice de dissimilarité (\( d_{ij} \))**

La fonction `create_dissimilarity_matrix()` génère des combinaisons de deux sujets cités (\( T_i \), \( T_j \)) et calcule leur dissimilarité en fonction de leur niveau hiérarchique (topics, subfields, fields, domains). La distance \( d_{ij} \) entre deux sujets est calculée avec des poids spécifiques attribués à chaque niveau :

- **Topics** (même sujet) : distance \( d = 0 \)
- **Subfields** : distance \( d = 0.1 \)
- **Fields** : distance \( d = 0.4 \)
- **Domains** : distance \( d = 0.8 \)
- **Max** (aucun lien commun) : distance \( d = 1 \)

Ensuite, l'ensemble des dissimilarités est moyenné pour donner une **dissimilarité moyenne** (\( \bar{d} \)) entre tous les sujets cités.

### 3. **Calcul de l'indice de Rao-Stirling**

L'indice de Rao-Stirling mesure l'interdisciplinarité en combinant les proportions des sujets \( p_i \) et \( p_j \) avec la dissimilarité entre eux \( d_{ij} \). La formule est la suivante :

\[
RS = \sum_{i,j} p_i \cdot p_j \cdot d_{ij}
\]

Dans le script, cette formule est implémentée dans `calculate_rao_stirling_index()`. Pour chaque paire de sujets \( i \) et \( j \) dans les articles cités, le script multiplie la proportion \( p_i \) de chaque sujet par \( p_j \), puis par la dissimilarité \( d_{ij} \) entre eux.

### Exemple de calcul :

- **Proportions** : Supposons que les proportions des sujets soient \( p_1 = 0.3 \), \( p_2 = 0.2 \), \( p_3 = 0.5 \).
- **Dissimilarités** : Si les dissimilarités entre les sujets sont \( d_{12} = 0.1 \), \( d_{13} = 0.4 \), \( d_{23} = 0.8 \).
- **Indice de Rao-Stirling** :

\[
RS = (0.3 \cdot 0.2 \cdot 0.1) + (0.3 \cdot 0.5 \cdot 0.4) + (0.2 \cdot 0.5 \cdot 0.8) = 0.006 + 0.06 + 0.08 = 0.146
\]

### Conclusion

Le script calcule ainsi un score d'interdisciplinarité pour chaque article en se basant sur la répartition des sujets dans les articles cités et leur dissimilarité, permettant de mesurer la diversité disciplinaire d'un ensemble de publications.