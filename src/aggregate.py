import pandas as pd
from src.food2emissions import compute_emissions, import_data_from_agribalyse
from src.utils import DIST
from tqdm import tqdm
from typing import Callable, Dict, Tuple

EMISSION_TYPES = [
    "agriculture_co2",
    "transformation_co2",
    "packaging_co2",
    "transport_co2",
    "distribution_co2",
    "consumption_co2",
]

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
    print("\nProcessing ingredients...\n")
    for ing in tqdm(ing_all[1:], ncols=100):
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


def aggregate_data(recipes: Dict, distance: Callable = DIST["per"]) -> Tuple:

    products_data = import_data_from_agribalyse()
    ingredients_data = match_all_ingredients(recipes=recipes, distance=distance)

    # compute the total weight of each recipe

    for recipe_name, recipe in recipes.items():
        total_weight = 0
        for weight in recipe["ingredients"].values():
            total_weight += weight
        recipes[recipe_name]["total_weight"] = total_weight

    # transform recipes

    recipes_data = pd.DataFrame(columns=["recipes", "name_prod", "weights"])

    for recipe_name, recipe in recipes.items():
        for ingredient_name, weight in recipe["ingredients"].items():
            recipes_data = recipes_data.append(
                {
                    "recipes": recipe_name,
                    "name_prod": ingredient_name,
                    "weights": weight / recipe["total_weight"],
                    "score": recipe["score"],
                },
                ignore_index=True,
            )

    # aggregate data

    output = (
        recipes_data.merge(ingredients_data, on=["name_prod"])
        .merge(
            products_data,
            left_on=["agribalyse_match"],
            right_on=["name_prod"],
            how="left",
        )
        .drop(columns=["name_prod_y", "clean_name_prod"])
        .rename(columns={"name_prod_x": "ingredients"})
    )

    output = pd.melt(
        output,
        id_vars=[
            "recipes",
            "ingredients",
            "weights",
            "score",
            "agribalyse_match",
            "distance",
            "dqr",
        ],
        value_vars=[
            "agriculture_co2",
            "transformation_co2",
            "packaging_co2",
            "transport_co2",
            "distribution_co2",
            "consumption_co2",
        ],
        var_name="emission_type",
        value_name="co2",
    )

    return output
