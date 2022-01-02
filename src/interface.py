import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from src.aggregate import EMISSION_TYPES


def preprocess_data(recipe_emissions, recipe_uncertainty, ingredients_figures):

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

    return recipe_data, ingredients_data


def compare_recipes(recipe_data):

    fig = go.Figure(
        data=[
            go.Bar(
                x=recipe_data["recipe"],
                y=recipe_data["emissions"],
                name="Émissions de CO2 (gCO2eq/g)",
                yaxis="y1",
            ),
            go.Scatter(
                x=recipe_data["recipe"],
                y=recipe_data["uncertainty"],
                name="Incertitude",
                yaxis="y2",
            ),
        ],
        layout=go.Layout(
            title="Émissions de CO2 par recette (gCO2eq/g)",
            yaxis={"title": "gCO2eq/g"},
            yaxis2={"title": "Incertitude", "overlaying": "y", "side": "right"},
        ),
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
