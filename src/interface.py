import pandas as pd
import plotly
import plotly.express as px


def preprocess_data(aggregated_data : pd.DataFrame) -> pd.DataFrame:
    """prettify the data to make it more readable

    Args:
        aggregated_data (pd.DataFrame): aggregated data

    Returns:
        pd.DataFrame: prettified data
    """

    aggregated_data = aggregated_data.rename(
        columns={
            "recipes": "Recette",
            "ingredients": "Ingrédient",
            "weights": "Masse (g)",
            "nb_comments": "Nombre de commentaires",
            "mark": "Note de la recette",
            "url": "Lien",
            "agribalyse_match": "Meilleure correspondance Agribalyse",
            "distance": "Fiabilité de la correspondance Agribalyse (%)",
            "dqr": "Qualité des données (1 : très fiable, 5 : peu fiable)",
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

    aggregated_data["Note de la recette"] = aggregated_data["Note de la recette"].round(
        1
    )

    aggregated_data["Masse (g)"] = (
        1000 * aggregated_data["Masse (g)"]
    ).round()  # the weights of the ingredients in grams correspond to 1 kg = 1000 g of food

    aggregated_data["Émissions de CO2 (kgCO2eq)"] = (
        aggregated_data["Émissions de CO2 (kgCO2eq)"]
    ).round(2)

    aggregated_data["Fiabilité de la correspondance Agribalyse (%)"] = (
        (1 - aggregated_data["Fiabilité de la correspondance Agribalyse (%)"]) * 100
    ).round()

    aggregated_data[
        "Qualité des données (1 : très fiable, 5 : peu fiable)"
    ] = aggregated_data["Qualité des données (1 : très fiable, 5 : peu fiable)"].round(
        2
    )

    return aggregated_data


def compare_recipes(data : pd.DataFrame) -> px.bar:
    """display a bar plot comparing the different recipes

    Args:
        data (pd.DataFrame): prettified data

    Returns:
        px.bar: plotly figure ready to be displayed
    """

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

    data["Recette"] = (
        '<a href="'
        + data["Lien"]
        + '"><b>'
        + data["Recette"]
        + "</b></a><br>"
        + data["Nombre de commentaires"].astype(str)
        + " commentaires • "
        + data["Note de la recette"].astype(str)
        + " sur 5"
    )

    fig = px.bar(
        data,
        x="Recette",
        y="Émissions de CO2 (kgCO2eq) par kg de plat",
        color="Ingrédient",
        title="<b>Émissions de CO2 par recette (pour 1 kg)</b>",
        hover_data=[
            "Masse (g)",
            "Meilleure correspondance Agribalyse",
            "Fiabilité de la correspondance Agribalyse (%)",
            "Qualité des données (1 : très fiable, 5 : peu fiable)",
            "Émissions de CO2 (kgCO2eq) par kg d'ingrédient",
        ],
    )
    fig.update_layout(xaxis={"categoryorder": "total descending"})
    return fig


def compare_ingredients(data : pd.DataFrame) -> px.bar:
    """display a bar plot comparing the different ingredients

    Args:
        data (pd.DataFrame): prettified data

    Returns:
        px.bar: plotly figure ready to be displayed
    """

    data = data[
        [
            "Ingrédient",
            "Meilleure correspondance Agribalyse",
            "Fiabilité de la correspondance Agribalyse (%)",
            "Qualité des données (1 : très fiable, 5 : peu fiable)",
            "Type d'émissions de CO2",
            "Émissions de CO2 (kgCO2eq)",
        ]
    ]

    data = data.drop_duplicates()

    fig = px.bar(
        data,
        x="Ingrédient",
        y="Émissions de CO2 (kgCO2eq)",
        color="Type d'émissions de CO2",
        title="<b>Émissions de CO2 par ingrédient (pour 1 kg)</b>",
        hover_data=[
            "Meilleure correspondance Agribalyse",
            "Fiabilité de la correspondance Agribalyse (%)",
            "Qualité des données (1 : très fiable, 5 : peu fiable)",
        ],
    )
    fig.update_layout(xaxis={"categoryorder": "total descending"})
    return fig


def interface(data : pd.DataFrame) -> None:
    """create a html file combining two Plotly figures

    Args:
        data (pd.DataFrame): prettified data

    Returns:
        None
    """

    fig1 = compare_recipes(data)
    fig2 = compare_ingredients(data)

    with open("data/interface.html", "w") as interface:

        interface.write("<html><head></head><body>" + "\n")
        for fig in (fig1, fig2):
            inner_html = fig.to_html().split("<body>")[1].split("</body>")[0]
            interface.write(inner_html)
        interface.write("</body></html>" + "\n")

    print(
        """
    ###################################################################
    ### L'interface a été générée avec succès : data/interface.html ###
    ###################################################################
    """
    )
