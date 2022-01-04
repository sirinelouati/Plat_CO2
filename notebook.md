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
    Etape 1: Implémentation d'un scrapper 
    Etape 2: Extraction de données et calcul de l'empreinte carbone des récettes
    Etape 3: Visualisation des résultats




## Les importations

Nous travaillons à partir du fichier main qui synthétise toutes les étapes de notre programme.



```python
from main import main
```

## Etape 1: Implémentation d'un scrapper 


Nous présentons à l'aide d'un exemple simple l'utilisation du scrapper marmiton.

*Si l'utiliseur rentre "Gâteau au chocolat" que renvoie notre scrapper ?*

```python
from src.dummy import dummy_output1
dummy_output1
```

<!-- #region -->
*Construction d'un  indicateur de confiance*

Pour évaluer la fiabilité des différentes recettes, nous avons décidé de construire un indicateur de confiance basé sur la note de la recette sur marmiton ainsi que sur le nombre de commentaires associés à la recette.

*Dificultés survenues*

L'une des premières difficultés survenues lors de l'implémentation du scrapper fut les blocages d'accès du site marmiton. Pour éviter ces blocages à répétitions nous avons du recourir à quelques astuces (on peut citer par exemple l'utilisation de firefox, de la fonction sleep() pour simuler un comportement utilisateur). Par ailleurs, nous avons du surmonter certaines difficultés inattendues comme l'apparition potenteille de cookie, de condition d'ulisations ou encore les mises à jours du sites qui peuvent rapidement rendre obsolètes notre scrapper (possibilité qui peut en partie etre éviter en utilisant de manière judicieuse les chemins du site).


*Limites du Scrapper*

Dans la partie scrapping de notre projet certaines simplifications ont été nécéssaires  pour mener à bien notre projet. Tout d'abord, nous avons fait le choix de nous restreindre aux recettes issu du site "Marmiton", du fait de la variété de recettes associées à un plat.
Cependant il aurait pu etre interressant d'utiliser des recettes de différents sites mais pour des raisons de simplicité et de complexité algorithme nous nous sommes concentrés sur les recettes proposées par Marmiton.
De plus, notre scrapper se devait de renvoyer un dictionnaire dans lequel chaque ingrédients était associé à son poids correspondnat dans la recette. Il a donc fallu procéder à des conversions et à certaines simplications pour rendre compte du poids de certaines quantités qui ne sont exprimées en gramme, par exemple les ingrédients du type (' 1 sachet de levure ', ' 1 cuillers à café ' sont automatiquement asssocié à un poids de 11 grammes et 15 grammes).
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

A partir de la sortie Marmiton obtenue via le scrapper, comment peut-on obtenir l'empreinte carbone d'une recette ?

C'est l'objectif de la deuxième étape qui consiste à chercher les ingrédients de la base Agribalyse qui correspondent le mieux aux ingrédients de notre recette. Pour cela, nous utilisons des distances préexistantes comme le distance de Levenstein ou la distance issue du package fuzzywuzzy.

*Difficultés survenues*

Les distances utilisées donnent des matching pas très satisfaisants. En effet, en calculant des indices d'incertitudes, on se rend compte que les ingrédients disponibles dans Agribalyse ne correpondent pas à ceux de notre recette. 
Pour cela, nous créons une focntion distance personnalisée à la main qui renvoit de meilleurs résultats

*Limites*

Malgré l'utilisation d'une distance personnalisée, on observe toujours une incertitude au niveau du matching entre les ingrédients du site Agribalyse et ceux de la recette Marmiton. Par exemple, pour l'ingrédient "eau", l'ingrédient du site "Agribalyse" qui correspond le mieux est l'ingrédient "eau de vie" qui ne corresspond pas à ce qu'on attend.


Une idée d'amélioration serait potentiellement d'introduire de nouvelles distances ou d'utiliser du NLP pour optimiser le matching 


```python
from src.aggregate import match_all_ingredients, aggregate_data
match_all_ingredients
```
