from src.food2emissions import compute_emissions
from src.utils import DIST
import pandas as pd
from typing import Dict, Tuple

pd.options.mode.chained_assignment = (  # prevents pandas from sending seemingly useless warning messages
    None
)


def match_all_ingredients(recipes: Dict) -> pd.DataFrame:
    """Finds the emissions figures that best match with the ingredients found by the scrappers.

    Args:
        recipes (Dict): output of the scrappers

    Returns:
        pd.DataFrame: best emission figures for each ingredient
    """

    # get the list of all ingredients used in the recipes
    ing_all = list(
        set(
            ing
            for ing_list in [
                list(recipe["ingredients"].keys())
                for website_list in recipes.values()
                for recipe in website_list
            ]
            for ing in ing_list
        )
    )

    # compute the emissions figures for each of them
    ing_data = compute_emissions(ing_all[0])
    for ing in ing_all[1:]:
        ing_data = ing_data.append(compute_emissions(ing), ignore_index=True)

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
                    DIST["fwz"](prod_name, prod),
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
    (ing_agg["best"], ing_agg["agribalyse_match"]) = zip(
        *pd.Series(
            ing_agg.apply(
                lambda x: (x["name_prod"], x["agribalyse_match"])
                if (
                    x["uncertainty"] < x["distance_to_closest"]
                    or x["uncertainty"] < x["closest_uncertainty"]
                )
                else (x["closest"], x["closest_agribalyse_match"]),
                axis=1,
            )
        )
    )

    return ing_agg
