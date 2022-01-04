---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.13.5
  kernelspec:
    display_name: 'Python 3.7.1 64-bit (''base'': conda)'
    language: python
    name: python3
---

# **Projet Python 2A**
Jean Baptiste Laval - Sirine Louati - Hadrien Lolivier

*Ce projet est réalisé dans le cadre du cours de python de Lino Galiana pour l'année 2021-2022.*

<div align="center">
  <img src="https://www.planete-energies.com/sites/default/files/styles/media_full_width_940px/public/thumbnails/image/visuel_emissions_co2_small.jpg?itok=Rrh1f3Qy"><br>
</div>
-----------------


## Introduction

**L'objectif** de notre programme est de retourner l'empreinte carbone de différentes recettes d'un plat choisi à la discrétion de  l'utilisateur. Ainsi, en rentrant le nom d'un plat, notre programme a pour mission de rendre compte de l'impact carbone de ce dernier à travers differents indicateurs et différentes recettes. Notre algorithme se décompose en trois grandes étapes :

    Etape 1: Implémentation d'un scraper 
    Etape 2: Extraction de données et calcul de l'empreinte carbone des recettes
    Etape 3: Visualisation des résultats




## Les importations

Nous travaillons à partir du fichier main qui synthétise toutes les étapes de notre programme.



```python
from main import main
```

## Etape 1: Implémentation d'un scraper 


Nous présentons à l'aide d'un exemple simple l'utilisation du scraper marmiton.

*Si l'utiliseur rentre "Gâteau au chocolat" que renvoie notre scraper ?*

```python
from src.dummy import dummy_output1
dummy_output1
```

<!-- #region -->
*L'idée de l'étape scraping*

Quand un utilisateur tape "Gâteau au chocolat", notre scraper visite le site marmiton, en extrait plusieurs recettes associées à "Gâteau au chocolat" et les renvoient sous forme de dictionnaire de dictionnaires contenant respectivement les ingrédients de la recette (convertis en grammes), son nombre de personnes, son nombre de commentaires, sa note marmiton et son lien url.

*Construction d'un  indicateur de confiance*

Pour évaluer la fiabilité des différentes recettes, nous avons décidé d'extraire la note de la recette sur Marmiton ainsi que son nombre de commentaires.

*Dificultés survenues*

L'une des premières difficultés survenues lors de l'implémentation du scrapper fut les blocages d'accès du site marmiton. Pour éviter ces blocages à répétitions nous avons du recourir à quelques astuces (On peut citer par exemple l'utilisation de Firefox, de la fonction `.sleep()` pour simuler un comportement utilisateur). Par ailleurs, nous avons dû surmonter certaines difficultés inattendues comme l'apparition potentielle de cookies, de condition d'utilisations ou encore les mises à jour du site qui peuvent rapidement rendre obsolètes notre scrapper (problème qui a pu en partie être résolu en utilisant de manière judicieuse les chemins du site).


*Limites du Scrapper*

Dans la partie scraping, certaines simplifications ont été nécessaires pour mener à bien notre projet. Tout d'abord, nous avons fait le choix de nous restreindre aux recettes issues du site "Marmiton", du fait de la variété de recettes associées à un plat.
Cependant, il aurait pu être intéressant d'utiliser des recettes de différents sites, mais pour des raisons de simplicité et de complexité algorithme nous nous sommes concentrés sur les recettes proposées par Marmiton.
De plus, notre scraper se devait de renvoyer un dictionnaire dans lequel chaque ingrédient était associé à son poids correspondant dans la recette. Il a donc fallu procéder à des conversions et à certaines simplifications pour rendre compte du poids de certaines quantités qui ne sont pas naturellement exprimées en gramme, par exemple les ingrédients du type ('1 sachet de levures ', ' 1 cuiller à café ' sont automatiquement associés à un poids de 11 grammes et 15 grammes.).
<!-- #endregion -->

## Etape 2: Extraction de données et calcul de l'empreinte carbone des récettes

```python
from src.dummy import dummy_aggregated_data
dummy_aggregated_data
```

```python
main()
```

*But*
calcul empreinte carbone en les asociant à la bonne base agribalyse ...
Difficulté à surmonter associé les bons ingrédients ...

```python
from src.aggregate import match_all_ingredients, aggregate_data
match_all_ingredients
```
