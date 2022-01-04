<div align="center">
  <img src="https://www.planete-energies.com/sites/default/files/styles/media_full_width_940px/public/thumbnails/image/visuel_emissions_co2_small.jpg?itok=Rrh1f3Qy"><br>
</div>

-----------------


# Plat CO2
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

La première focntion que nous implémentons `preprocess_data` permet de nettoyer la base de sortie de l'étape d'aggrégation. En effet, on renomme les colonnes en français et en format plus compréhensible, on rajoute des majuscules et les unités corrspondantes, on arrondit les chiffres et on considére que le poids des ingrédients en gramme correspond à celui nécessaire pour préparer 1 kilo du plat en question.

Par la suite, nous implémentons les deux fonctions primordiales de cette dernière partie:

- la fonction `compare_recipes` permet de renvoyer une première figure d'un histogramme où chaque colonne correspond à une recette du plat en question.

```python
from src.interface import compare_recipes
```
- la fonction `compare_ingredients` permet de renvoyer une seconde figure d'un hidtogramme où chauqe colonne correspond à un ingrédient parmi tous les ingrédients confondus de toutes les recettes.

```python
from src.interface import compare_ingredients
```

Le premier histogramme permet de rendre compte des recettes les plus carbonées et les moins carbonées. Et parfois, certaines recettes peuvent être carbonées à cause d'un ingrédient en particulier sans comprendre pourquoi cet ingrédient est très carboné. Pour cela, le second histogramme permet d'expliquer ce point et voir les différents postes d'émissions de chaque ingrédient.

La dernière fonction `interface` permet de fusionner les deux histogrammes sous format html. Sur la page html, en passant la souris sur chaque recette, on peut visualiser chaque ingrédient qui la compose avec des informations complémentaires: la recette en question, le nombre de commentaires et la note attribuée sur le site Marmiton, les émissions carbone de l'ingrédient et du plat, la quantité de l'ingrédient en gramme pour préparer un kilo du plat, la meilleure correspondance avec la base Agribalyse et le dregré de fiabilité de cette correspondance.

Par ailleurs, en cliquant sur le nom de chaque recette en bas du premier histogramme, cela permet de se diriger vers le site Marmiton et d'ouvrir la page de la recette en question. 

En parcourant le deuxième histogramme à la souris, on obtient également les mêmes informations supplémentaires que pour le premier et en précisant également les proportions des postes d'émission carbone de chaque ingrédient.






