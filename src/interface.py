import pandas as pd
import plotly.express as px
from src.aggregate import EMISSION_TYPES


def preprocess_data(
    recipe_emissions, recipe_uncertainty, ingredients_figures, cross_emissions
):

    recipe_data = recipe_emissions.merge(recipe_uncertainty, on="recipe")[
        ["recipe", "total_co2", "weighted_average"]
    ].rename(columns={"total_co2": "emissions", "weighted_average": "uncertainty"})

    ingredients_data = pd.melt(
        ingredients_figures,
        id_vars=["product", "uncertainty"],
        value_vars=EMISSION_TYPES,
        var_name="emission_type",
        value_name="co2",
    )

    cross_data = pd.melt(
        cross_emissions,
        id_vars=["recipe"],
        var_name="ingredient",
        value_name="co2",
    )

    return recipe_data, ingredients_data, cross_data


def compare_recipes(cross_data):

    fig = px.bar(
        cross_data,
        x="recipe",
        y="co2",
        color="ingredient",
        title="Émissions de CO2 par recette (gCO2eq/g)",
    )
    fig.show()


def compare_ingredients(ingredients_data):

    fig = px.bar(
        ingredients_data,
        x="product",
        y="co2",
        color="emission_type",
        title="Émissions de CO2 par ingrédient (gCO2eq/g)",
    )
    fig.show()
