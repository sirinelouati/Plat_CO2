import pandas as pd
import plotly.express as px
from src.aggregate import EMISSION_TYPES


def preprocess_data(
    recipe_emissions, recipe_uncertainty, ingredients_figures, cross_emissions
):

    recipe_data = recipe_emissions.merge(recipe_uncertainty, on="recipe")[
        ["recipe", "total_co2", "weighted_average"]
    ].rename(
        columns={
            "recipe": "Recette",
            "total_co2": "Émissions de CO2 (kgCO2eq)",
            "weighted_average": "Incertitude",
        }
    )

    ingredients_data = pd.melt(
        ingredients_figures,
        id_vars=["product", "uncertainty"],
        value_vars=EMISSION_TYPES,
        var_name="Type d'émission de CO2",
        value_name="Émissions de CO2 (kgCO2eq)",
    ).rename(columns={"product": "Ingrédient", "uncertainty": "Incertitude"})

    ingredients_data["Type d'émission de CO2"] = (
        ingredients_data["Type d'émission de CO2"]
        .str.capitalize()
        .str.replace("_co2", "")
    )

    ingredients_data["Ingrédient"] = ingredients_data["Ingrédient"].str.capitalize()

    cross_data = pd.melt(
        cross_emissions,
        id_vars=["recipe"],
        var_name="Ingrédient",
        value_name="Émissions de CO2 (khCO2eq)",
    ).rename(columns={"recipe": "Recette"})

    return recipe_data, ingredients_data, cross_data


def compare_recipes(cross_data):

    fig = px.bar(
        cross_data,
        x="Recette",
        y="Émissions de CO2 (khCO2eq)",
        color="Ingrédient",
        title="Émissions de CO2 par recette (pour 1 kg)",
    )
    fig.show()


def compare_ingredients(ingredients_data):

    fig = px.bar(
        ingredients_data,
        x="Ingrédient",
        y="Émissions de CO2 (kgCO2eq)",
        color="Type d'émission de CO2",
        title="Émissions de CO2 par ingrédient (pour 1 kg)",
    )
    fig.show()
