<div align="center">
  <img src="https://www.planete-energies.com/sites/default/files/styles/media_full_width_940px/public/thumbnails/image/visuel_emissions_co2_small.jpg?itok=Rrh1f3Qy"><br>
</div>

-----------------


# Plat_CO2
Ce projet est réalisé dans le cadre du cours de python de Lino Galiana 2021-2022.

Il s'agit d'un programme qui permet de renvoyer à l'utilisateur la recette avec l'émission en carbone la plus faible parmi toutes les recettes disponibles sur le site "Marmitton"


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

1. La première partie du projet consiste à scrapper le site "Marmitton".
Nous avons utiliser le package `selenium`.
Le scrapper commence par accepter les cookies s'ils existent, puis se dirige vers les résultats de recherche et sur les recettes correspondantes.
Ensuite, à partir de chaque recette, on crée un dictionnaire dont la clé est l'ingrédient et la valeur une liste contenant la quantité et son unité.
Par exemple pour une recette de gateau au chocolat, on obtient:
`{'sucre semoule': [120.0, 'g'], 'sucre vanillé': [1.0, 'paquet'], 'levure chimique': [0.5, 'paquet'], 'farine': [125.0, 'g'], 'colza': [0.5, 'verre'], 'pommes': [3.0], 'oeufs': [3.0]}`
L'idée ensuite est de nettoyer les noms des ingrédients (par exemple enlever "+ monter en neige") et convertir toutes les unités en gramme (par exemple les sachets de levure ou le nombre d'oeufs). Pour cela, nous créeons un annuaire permettant de convertir le nombre de fruits et de légumes, les paquets, sachets, tasses, verres, cuillères à café, cuillères à soupe en gramme.
Par ailleurs, nous procédons également à une lematisation en utilisant le package `nltk` afin d'éviter les problèmes relatifs à la mise au pluriel des ingrédients.

3. La deuxième partie consiste à extraire la base de données du site "Agribalyse" disponible sous format "csv".
Nous commençons par importer la base de données à partir du site "Agribalyse":
("https://koumoul.com/s/data-fair/api/v1/datasets/agribalyse-detail-etape/raw").
Ensuite, nous renommons les colonnes de la base pour les rendre plus compréhensibles. Nous procédons également au nettoyage des noms des ingrédients afin de les rendre les plus proches possible à ce de la base de données. Pour cela, nous retirons les accents, les majuscules et nous gardons que les lettres et les espaces. Tous ces instructions sont effectuées par la fonction `clean_string`.
Par la suite, la focntion `match_products` permet de renvoyer les noms d'ingrédients de la base de données les plus proches de notre ingrédient initial

5. La dernière partie est une visualisation graphique des données.

## Contribution



## Licence
