import pandas as pd
from src.food2emissions import compute_emissions, import_data_from_agribalyse
from src.utils import DIST
from typing import Callable, Dict, Tuple

pd.options.mode.chained_assignment = (  # prevents pandas from sending seemingly useless warning messages
    None
)


#########################################################
### COMPARE THE RECIPES TO BEST MATCH THE INGREDIENTS ###
#########################################################


def match_all_ingredients(
    recipes: Dict, distance: Callable = DIST["per"]
) -> pd.DataFrame:
    """Finds the emissions figures that best match with the ingredients found by the scrappers.

    Args:
        recipes (Dict): output of the scrappers
        distance (Callable): function that computes a distance between two strings. Its value is 0
            for a perfect match, 1 in the worst case. Defaults to Levenshtein's distance.

    Returns:
        pd.DataFrame: best emission figures for each ingredient
    """

    # get the list of all ingredients used in the recipes
    ing_all = list(
        set(  # to remove duplicates
            ing
            for ing_list in [
                list(recipe["ingredients"].keys()) for recipe in recipes.values()
            ]
            for ing in ing_list
        )
    )

    # compute the emissions figures for each of them
    ing_data = compute_emissions(ing_all[0], distance=distance)
    for ing in ing_all[1:]:
        ing_data = ing_data.append(
            compute_emissions(ing, distance=distance), ignore_index=True
        )

    ing_agg = ing_data[["name_prod", "uncertainty", "agribalyse_match"]]

    # this function is used just after
    def get_closest(prod_name: str) -> Tuple:
        """Finds the closest ingredient to 'prod_name' in 'ing_agg' and returns its name, its distance to 'prod_name', its uncertainty and the matching ingredient among Agribalyse data.

        Args:
            prod_name (str): the name of the given ingredient

        Returns:
            Tuple: name, distance to the given ingredient, uncertainty and matching Agribalyse product of the closest ingredient
        """

        return min(
            [
                (
                    prod,
                    distance(prod_name, prod),
                    ing_agg[ing_agg["name_prod"] == prod].iloc[0]["uncertainty"],
                    ing_agg[ing_agg["name_prod"] == prod].iloc[0]["agribalyse_match"],
                )
                for prod in ing_agg["name_prod"]
                if prod != prod_name
            ],
            key=lambda x: (x[1], x[2]),
        )

    # for each ingredient, computes the closest ingredient
    (
        ing_agg["closest"],
        ing_agg["distance_to_closest"],
        ing_agg["closest_uncertainty"],
        ing_agg["closest_agribalyse_match"],
    ) = zip(
        *pd.Series(
            ing_agg["name_prod"].apply(get_closest).to_list(),
        )
    )

    # keeps an ingredient, or replaces it by the closest one
    output = pd.DataFrame()

    (output["name_prod"], output["agribalyse_match"], output["distance"]) = zip(
        *pd.Series(
            ing_agg.apply(
                lambda x: (x["name_prod"], x["agribalyse_match"], x["uncertainty"])
                if (
                    x["uncertainty"] < x["distance_to_closest"]
                    or x["uncertainty"] < x["closest_uncertainty"]
                )
                else (
                    x["name_prod"],
                    x["closest_agribalyse_match"],
                    max(x["closest_uncertainty"], x["distance_to_closest"]),
                ),
                axis=1,
            )
        )
    )

    return output


######################################################
### COMPUTE THE AGGREGATED FIGURES FOR EACH RECIPE ###
######################################################


def compute_recipes_figures(recipes : Dict, distance : Callable = DIST["per"]) -> Tuple:
    
    products_data = import_data_from_agribalyse()
    ingredients = match_all_ingredients(recipes=recipes, distance=distance)

    ingredients_figures = ingredients.merge(products_data, left_on="agribalyse_match", right_on="name_prod", how="left").drop(['agribalyse_match', "name_prod_y", "clean_name_prod"], axis=1).rename(columns={"name_prod_x":"product"})

    ingredients_figures["uncertainty"] = ingredients_figures["distance"] / 2 + (ingredients_figures["dqr"] - 1) / 8

    for recipe_name, recipe in recipes.items():
        for ingredient, weight in recipe["ingredients"].items():
            recipes[recipe_name]["ingredients"][ingredient] = weight / recipe["nb_people"]
            recipes[recipe_name]["nb_people"] = 1

    recipes_figures = pd.DataFrame()

    for recipe_name, recipe in recipes.items():

        emission_denominator = 0

        for ingredient, weight in recipe['ingredients'].items():
            emission_denominator += weight * ingredients_figures[ingredients_figures["product"] == ingredient].iloc[0]["uncertainty"]
        
        recipe_emissions = {"recipe": recipe_name}
        for emission_type in ingredients_figures:
            if emission_type.endswith("co2"):
                emission = 0
                for ingredient, weight in recipe['ingredients'].items():
                    emission += weight * ingredients_figures[ingredients_figures["product"] == ingredient].iloc[0]["uncertainty"] * ingredients_figures[ingredients_figures["product"] == ingredient].iloc[0][emission_type]
                emission /= emission_denominator
                recipe_emissions[emission_type] = emission
        
        recipes_figures = recipes_figures.append(recipe_emissions, ignore_index=True)
    
    print(recipes_figures)