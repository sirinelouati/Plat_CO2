<div align="center">
  <img src="https://www.planete-energies.com/sites/default/files/styles/media_full_width_940px/public/thumbnails/image/visuel_emissions_co2_small.jpg?itok=Rrh1f3Qy"><br>
</div>

-----------------


# Plat_CO2
Ce projet est réalisé dans le cadre du cours de python de Lino Galiana 2021-2022.

Il s'agit d'un programme qui permet de renvoyer à l'utilisateur la recette avec l'émission en carbone la plus faible parmi toutes les recettes disponibles sur le site "Marmiton"


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
Nous rajoutons également une note de fiabilité de la recette correspondant à la note attribuée par les utilisateurs sur Marmiton et à leurs commentaires (avec une pondération 60% commentaires et 40% note) qui nous permettront par la suite de pondérer les recettes.
L'idée ensuite est de nettoyer les noms des ingrédients (par exemple enlever "+ monter en neige") et convertir toutes les unités en gramme (par exemple les sachets de levure ou le nombre d'oeufs). Pour cela, nous créeons un annuaire permettant de convertir le nombre de fruits et de légumes, les paquets, sachets, tasses, verres, cuillères à café, cuillères à soupe en gramme.
Par ailleurs, nous procédons également à une lematisation en utilisant le package `nltk` afin d'éviter les problèmes relatifs à la mise au pluriel des ingrédients.
Nous rajoutons également dans le dictionnaire la note de fiabilité, le nombre de personnes et l'URL de la recette pour obtenir par exemple le dictionnaire suivant:
`{0: {'nombre_personne': 6,
  'note_fiabilite_recette': 0.976,
  'recette_ingredients': {'beurre': [100.0, 'g'],
   'chocolat': [200.0, 'g'],
   'farin': [50.0, 'g'],
   'oeuf': [210.0, 'g'],
   'sucre': [100.0, 'g']},
  'url_recette': 'https://www.marmiton.org/recettes/recette_gateau-au-chocolat-fondant-rapide_166352.aspx'},
 1: {'nombre_personne': 8,
  'note_fiabilite_recette': 0.976,
  'recette_ingredients': {'beurre': [125.0, 'g'],
   'chocolat': [200.0, 'g'],
   'farin': [100.0, 'g'],
   'levure': [11.0, 'g'],
   'oeuf': [280.0, 'g'],
   'sucre': [200.0, 'g']},
  'url_recette': 'https://www.marmiton.org/recettes/recette_gateau-au-chocolat-des-ecoliers_20654.aspx'}}`

2. La deuxième partie consiste à extraire la base de données du site "Agribalyse" disponible sous format "csv".
Nous commençons par importer la base de données à partir du site "Agribalyse":
("https://koumoul.com/s/data-fair/api/v1/datasets/agribalyse-detail-etape/raw").
Ensuite, nous renommons les colonnes de la base pour les rendre plus compréhensibles. Nous procédons également au nettoyage des noms des ingrédients afin de les rendre les plus proches possible de ceux de la base de données. Pour cela, nous retirons les accents, les majuscules et nous gardons que les lettres et les espaces. Tous ces instructions sont effectuées par la fonction `clean_string`.
Par la suite, la focntion `match_products` permet de renvoyer les noms d'ingrédients de la base de données les plus proches de notre ingrédient initial.
Pour cela, nous utilisons trois distances normalisées (la distance est égale à 0 dans le meilleur des cas et à 1 dans le pire des cas pour pouvoir comparer les distances entre elles) possibles :
- la distance issue du package `difflib`: `SequenceMatcher` consiste à trouver la séquence commune maximale aux deux chaines de caractères à comparer
- la distance issue du package `fuzzywuzzy.fuzz`cacule la distance de levenshtein entre le mot le plus court et tous les sous mots du deuxième mot de même longueur que le premier mot et ensuite prend le minimum de toutes ces distances de levenshtein
- la distance de levenshtein issue du package `nltk' qui correpond à la distance qui minimise le nombre d'opérations à effectuer parmi 3 opérations: enlever, rajouter ou remplacer une chaine de caractère.

3. La dernière partie est une visualisation graphique des données.

## Contribution



## Licence
