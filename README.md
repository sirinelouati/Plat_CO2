<div align="center">
  <img src="https://www.planete-energies.com/sites/default/files/styles/media_full_width_940px/public/thumbnails/image/visuel_emissions_co2_small.jpg?itok=Rrh1f3Qy"><br>
</div>

-----------------


# Plat_CO2
Ce projet est réalisé dans le cadre du cours de python de Lino Galiana pour l'année 2021-2022.

Il s'agit d'un programme qui permet de comparer les émissions carbone des recettes d'un plat fourni par l'utilisateur à partir du site "Marmiton"


## Installation

Python 3.7 est requis.

Installation des modules :

```sh
pip install -r requirements.txt
```


## Utilisation (provisoire)

Une démonstration des fonctions principales est proposée dans le fichier `main.txt`.

```sh
python3 main.py
```

Pour tester le code, importez les fonctions voulues dans `main.py` et exécutez-les depuis ce fichier. L'exécution directe des fichiers du dossier `src` peut engendrer des erreurs d'importation.

## Résumé

1. La première partie du projet consiste à scrapper le site "Marmiton".

Nous avons utiliser le package `selenium`.
Le scrapper commence par accepter les cookies s'ils existent, puis se dirige vers les résultats de recherche et sur les recettes correspondantes.

Ensuite, à partir de chaque recette, on crée un dictionnaire dont la clé est l'ingrédient et la valeur une liste contenant la quantité et son unité.
Par exemple pour une recette de gateau au chocolat, on obtient:
`{'sucre semoule': [120.0, 'g'], 'sucre vanillé': [1.0, 'paquet'], 'levure chimique': [0.5, 'paquet'], 'farine': [125.0, 'g'], 'colza': [0.5, 'verre'], 'pommes': [3.0], 'oeufs': [3.0]}`

Nous calculons également une note de fiabilité de la recette correspondant à la note attribuée par les utilisateurs sur Marmiton et à leurs commentaires (avec une pondération 60% nombres de commentaires et 40% note) qui nous permettront par la suite de pondérer les recettes.

L'idée ensuite est de nettoyer les noms des ingrédients (par exemple enlever "+ monter en neige") et convertir toutes les unités en gramme (par exemple les sachets de levure, le nombre d'oeufs ou encore les autres unités). Pour cela, nous créeons un annuaire permettant de convertir le nombre de fruits et de légumes, les paquets, sachets, tasses, verres, cuillères à café, cuillères à soupe en gramme. Pour les ingrédients qui ne figurent pas dans notre annuaire, nous les associons à l'ingrédient le plus proche selon une distance personnalisée ou nous les stockons dans une liste (une amélioration possible serait d'enrichir notre annuaire au fur et à mesure que nous trouvions un nouvel ingrédient).
La distance personnalisée est une distance qui va de 0 à 1:
- 0: les chaines de caractères sont identiques
- de 0 à 0.2: une chaine de caractères commence par l'autre (par exemple: "chocolat noir" et "chocolat noir à 40%")
- de 0.2 à 0.4: une chaine de caractères commence par le/les premiers mots de l'autre (par exemple: "chocolat noir" et "chocolat au lait")
- de 0.4 à 0.6: une chaine de caractères contient l'intégralité de l'autre chaine mais pas dès le début (par exemple: "chocolat noir" et "tablette de chocolat noir fourrée")
- de 0.6 à 0.8: une chaine de caractères contient les premiers mots de l'autre (par exemple: "chocolat noir" et "tablette de chocolat au lait")
- de 0.8 à 1: les autres cas possibles

Par ailleurs, nous procédons également à une lematisation en utilisant le package `nltk` afin d'éviter les problèmes relatifs à la mise au pluriel des ingrédients.

Nous rajoutons également dans le dictionnaire la note de fiabilité, le nombre de personnes et l'URL de la recette pour obtenir par exemple le dictionnaire suivant:

`{
    "Gâteau au chocolat fondant rapide": {
        "ingredients": {
            "chocolat pâtissier": 200.0,
            "farine": 50.0,
            "sucre en poudre": 100.0,
            "beurre ": 100.0,
            "oeufs": 210.0,
        },
        "nb_people": 6,
        "score": 0.976,
        "url": "https://www.marmiton.org/recettes/recette_gateau-au-chocolat-fondant-rapide_166352.aspx",
    },
    "Gâteau au chocolat des écoliers": {
        "ingredients": {
            "chocolat noir": 200.0,
            "sucre en poudre": 200.0,
            "farine": 100.0,
            "levure chimique": 11.0,
            "oeufs": 280.0,
            "beurre doux": 125.0,
        },
        "nb_people": 8,
        "score": 0.976,
        "url": "https://www.marmiton.org/recettes/recette_gateau-au-chocolat-des-ecoliers_20654.aspx",
    },
    "Petits gâteaux tout chocolat": {
        "ingredients": {
            "farine": 100.0,
            "sucre": 100.0,
            "oeufs": 210.0,
            "crème dessert au chocolat": 200.0,
            "beurre": 100.0,
            "moules à muffin ou des caissettes en papier": 250.0,
        },
        "nb_people": 9,
        "score": 0.5862,
        "url": "https://www.marmiton.org/recettes/recette_petits-gateaux-tout-chocolat_36095.aspx",
    },
    "Gâteau au chocolat (seulement pour les enfants!)": {
        "ingredients": {
            "sucre": 250.0,
            "farine": 250.0,
            "levure": 5.5,
            "sucre vanillé": 11.0,
            "oeufs": 350.0,
            "crème dessert au chocolat": 180.0,
            "beurre": 50.0,
        },
        "nb_people": 8,
        "score": 0.5794,
        "url": "https://www.marmiton.org/recettes/recette_gateau-au-chocolat-seulement-pour-les-enfants_41649.aspx",
    },
}`

2. La deuxième partie consiste à extraire la base de données du site "Agribalyse" disponible sous format "csv".
3. 
Nous commençons par importer la base de données à partir du site "Agribalyse":
("https://koumoul.com/s/data-fair/api/v1/datasets/agribalyse-detail-etape/raw").

Ensuite, nous renommons les colonnes de la base pour les rendre plus compréhensibles.

Nous procédons également au nettoyage des noms des ingrédients afin de les rendre les plus proches possible de ceux de la première partie. Pour cela, nous retirons les accents, les majuscules et nous gardons que les lettres et les espaces. Tous ces instructions sont effectuées par la fonction `clean_string`.
Par la suite, la fonction `match_products` permet de renvoyer les noms d'ingrédients de la base de données les plus proches de notre ingrédient initial.
Pour cela, nous nous intéressons à 4 distances normalisées (la distance est égale à 0 dans le meilleur des cas et à 1 dans le pire des cas pour pouvoir comparer les distances entre elles) possibles :
- la distance issue du package `difflib`: `SequenceMatcher` consiste à trouver la séquence commune maximale aux deux chaines de caractères à comparer
- la distance issue du package `fuzzywuzzy.fuzz`cacule la distance de levenshtein entre le mot le plus court et tous les sous mots du deuxième mot de même longueur que le premier mot et ensuite prend le minimum de toutes ces distances de levenshtein
- la distance de levenshtein issue du package `nltk' qui correpond à la distance qui minimise le nombre d'opérations à effectuer parmi 3 opérations: enlever, rajouter ou remplacer une chaine de caractère.
- la distance personnalisée.

Après vérification sur plusieurs exemples, la distance personnalisée semble retourner les meilleurs résultats, nous l'utilisons pour la fonction `match_products`.

Finalement, nous retournons l'estimation d'emission carbone d'un produit à partir de celle du produit de la base Agribalyse qui lui correspond le mieux.

3. La dernière partie est une visualisation graphique des données.

Nous commençons par obtenir les émissions carbone de tous les ingrédients fournis lors de la première étape grace à la fonction `compute_emissions` implémentée à la deuxième étape.

Puis nous calculons d'autres chiffres tel que l'incertitude pour chaque ingrédient, nous normalisons également les recettes pour une seule personne.

Ensuite nous calculons les estimateurs aggrégés d'emission carbone et d'incertitude pour chaque recette et nous en faisant des représentations graphiques


## Contribution



## Licence
