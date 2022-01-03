import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
from src.aggregate import EMISSION_TYPES


def preprocess_data(aggregated_data):

    aggregated_data = aggregated_data.rename(
        columns={
            "recipes": "Recette",
            "ingredients": "Ingrédient",
            "weights": "Masse (g)",
            "score": "Fiabilité de la recette (%)",
            "agribalyse_match": "Meilleure correspondance Agribalyse",
            "distance": "Fiabilité de la correspondance Agribalyse (%)",
            "dqr": "Qualité des données (1 = très fiable, 5 = peu fiable)",
            "emission_type": "Type d'émissions de CO2",
            "co2": "Émissions de CO2 (kgCO2eq)",
        }
    )

    aggregated_data[
        ["Recette", "Ingrédient", "Meilleure correspondance Agribalyse"]
    ] = aggregated_data[
        ["Recette", "Ingrédient", "Meilleure correspondance Agribalyse"]
    ].apply(
        lambda x: x.astype(str).str.capitalize()
    )

    aggregated_data["Type d'émissions de CO2"] = aggregated_data[
        "Type d'émissions de CO2"
    ].replace(
        [
            "agriculture_co2",
            "transformation_co2",
            "packaging_co2",
            "transport_co2",
            "distribution_co2",
            "consumption_co2",
        ],
        [
            "Agriculture",
            "Transformation",
            "Emballage",
            "Transport",
            "Distribution",
            "Consommation",
        ],
    )

    aggregated_data["Masse (g)"] = (
        1000 * aggregated_data["Masse (g)"]
    ).round()  # the weights of the ingredients in grams correspond to 1 kg = 1000 g of food

    aggregated_data["Émissions de CO2 (kgCO2eq)"] = (
        aggregated_data["Émissions de CO2 (kgCO2eq)"]
    ).round(2)

    aggregated_data["Fiabilité de la recette (%)"] = (
        aggregated_data["Fiabilité de la recette (%)"] * 100
    ).round()

    aggregated_data["Fiabilité de la correspondance Agribalyse (%)"] = (
        (1 - aggregated_data["Fiabilité de la correspondance Agribalyse (%)"]) * 100
    ).round()

    aggregated_data[
        "Qualité des données (1 = très fiable, 5 = peu fiable)"
    ] = aggregated_data["Qualité des données (1 = très fiable, 5 = peu fiable)"].round(
        2
    )

    return aggregated_data


def compare_recipes(data):

    data = data.drop("Type d'émissions de CO2", axis=1)

    data = data.groupby(
        list(data.columns[:-1]), as_index=False
    ).sum()  # total emissions for each ingredient for each recipe

    data["Émissions de CO2 (kgCO2eq) par kg d'ingrédient"] = data[
        "Émissions de CO2 (kgCO2eq)"
    ]

    data["Émissions de CO2 (kgCO2eq) par kg de plat"] = (
        data["Émissions de CO2 (kgCO2eq)"] * data["Masse (g)"] / 1000
    ).round(
        2
    )  # real emissions for each ingredient for each recipe

    fig = px.bar(
        data,
        x="Recette",
        y="Émissions de CO2 (kgCO2eq) par kg de plat",
        color="Ingrédient",
        title="Émissions de CO2 par recette (pour 1 kg)",
        hover_data=[
            "Masse (g)",
            "Meilleure correspondance Agribalyse",
            "Fiabilité de la correspondance Agribalyse (%)",
            "Qualité des données (1 = très fiable, 5 = peu fiable)",
            "Émissions de CO2 (kgCO2eq) par kg d'ingrédient",
        ],
    )
    fig.update_layout(xaxis={"categoryorder": "total descending"})
    fig.show()


def compare_ingredients(data):

    fig = px.bar(
        data,
        x="Ingrédient",
        y="Émissions de CO2 (kgCO2eq)",
        color="Type d'émissions de CO2",
        title="Émissions de CO2 par ingrédient (pour 1 kg)",
    )
    fig.update_layout(xaxis={"categoryorder": "total descending"})
    fig.show()


def get_html(data):

    fig_recipes = px.bar(
        data,
        x="Recettes",
        y="Émissions de CO2 (kgCO2eq)",
        color="Ingrédients",
        title="Émissions de CO2 par recette (pour 1 kg)",
    )
    fig_recipes.update_layout(
        barmode="stack", xaxis={"categoryorder": "total descending"}
    )

    fig_ingredients = px.bar(
        data,
        x="Ingrédients",
        y="Émissions de CO2 (kgCO2eq)",
        color="Type d'émission de CO2",
        title="Émissions de CO2 par ingrédient (pour 1 kg)",
    )
    fig_ingredients.update_layout(
        barmode="stack", xaxis={"categoryorder": "total descending"}
    )

    with open("data/dashboard.html", "w") as dashboard:

        dashboard.write("<html><head></head><body>" + "\n")
        for fig in (fig_recipes, fig_ingredients):
            inner_html = fig.to_html().split("<body>")[1].split("</body>")[0]
            dashboard.write(inner_html)
        dashboard.write("</body></html>" + "\n")
