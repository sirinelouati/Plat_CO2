from src.utils import clean_string, DIST
from os.path import isfile
import pandas as pd
from typing import Callable, Dict, List, Optional


###################
### DATA IMPORT ###
###################


AGRIBALYSE_DATA_URL = (
    "https://koumoul.com/s/data-fair/api/v1/datasets/agribalyse-detail-etape/raw"
)
# available on https://doc.agribalyse.fr/documentation/acces-donnees (last consulted on 7 Dec. 2021)

PATH_TO_DATA = "data/agribalyse.csv"


def import_data_from_agribalyse(replace: bool = False) -> pd.DataFrame:
    """Imports Agribalyse's database related to the CO2 emissions by life cycle step for each
    product. Doesn't do anything if the file data/agribalyse.csv already exists.

    Args:
        replace (bool): True to replace data/agribalyse.csv if it already exists. Defaults to False.

    Returns:
        pandas.DataFrame: reshaped dataframeit
    """

    if (
        isfile(PATH_TO_DATA) and not replace
    ):  # case 1 : the file already exists AND replace is False
        df = pd.read_csv(PATH_TO_DATA)

    else:  # case 2 : the file doesn't exist yet OR replace is True
        df = pd.read_csv(AGRIBALYSE_DATA_URL)
        df = df[
            [
                "Nom du Produit en Français",
                "DQR",
                "Changement climatique (kg CO2 eq/kg de produit) - Agriculture",
                "Changement climatique (kg CO2 eq/kg de produit) - Transformation",
                "Changement climatique (kg CO2 eq/kg de produit) - Emballage",
                "Changement climatique (kg CO2 eq/kg de produit) - Transport",
                "Changement climatique (kg CO2 eq/kg de produit) - Supermarché et distribution",
                "Changement climatique (kg CO2 eq/kg de produit) - Consommation",
            ]
        ]

        # Data structure :
        #   - name_prod : name of the product in french
        #   - dqr (data quality ratio) : assess the reliability of the figure from 1 (reliable) to
        #     5 (not reliable)
        #   - [STEP]_co2 : gives the amount of emissions related to the step [STEP] within the
        #     product's life cycle. Expressed in kg of CO2eq per kg of product.
        df = df.rename(
            columns={
                "Nom du Produit en Français": "name_prod",
                "DQR": "dqr",
                "Changement climatique (kg CO2 eq/kg de produit) - Agriculture": "agriculture_co2",
                "Changement climatique (kg CO2 eq/kg de produit) - Transformation": "transformation_co2",
                "Changement climatique (kg CO2 eq/kg de produit) - Emballage": "packaging_co2",
                "Changement climatique (kg CO2 eq/kg de produit) - Transport": "transport_co2",
                "Changement climatique (kg CO2 eq/kg de produit) - Supermarché et distribution": "distribution_co2",
                "Changement climatique (kg CO2 eq/kg de produit) - Consommation": "consumption_co2",
            }
        )

        df["clean_name_prod"] = df.apply(
            lambda x: clean_string(x.name_prod), axis=1
        )

        df.to_csv(PATH_TO_DATA, index=False)

    return df


################
### MATCHING ###
################


def match_products(
    product_name: str,
    products_data: pd.DataFrame = None,
    distance: Callable = DIST["per"],
    n: Optional[int] = 1,
) -> pd.DataFrame:
    """Returns the 'n' closest products to 'product_name' in 'products_data' according to the
        distance 'distance'.

    Args:
        product_name (str): name of a product
        products_data (pd.DataFrame): pandas DataFrame with the data related to a list of products.
            The column with the names of the products must be 'name_prod'. Defaults to None.
        distance (Callable): function that computes a distance between two strings. Its value is 0
            for a perfect match, 1 in the worst case. Defaults to Levenshtein's distance.
        n (int, optional) : number of products to keep. Defaults to 1.

    Returns:
        pd.DataFrame : pandas DataFrame (same structure than 'products_data') with the n closest
            products to 'product_name' according to the distance 'distance', sorted from the closest
            to the furthest.
    """

    if products_data is None:
        products_data = import_data_from_agribalyse()

    clean_product_name = clean_string(product_name)

    products_data["distance"] = products_data.apply(
        lambda x: distance(x.clean_name_prod, clean_product_name), axis=1
    )

    return products_data.sort_values("distance").head(n)


##########################
### METHODS COMPARISON ###
##########################


def compare_methods(
    words_list: List,
    products_data: pd.DataFrame = None,
    dist_dict: Dict = DIST,
    n: int = 1,
) -> None:
    """Compares the different normalized methods to compute string distance.

    Args:
        words_list (List): list of strings to compare the methods on
        products_data (pd.DataFrame): pandas DataFrame with the data related to a list of products.
            The column with the names of the products must be 'name_prod'. Defaults to None.
        dist_dict (Dict, optional): dictionnary of different normalised methods that compute string
            distances. Defaults to DIST.
        n (int, optional): number of products to keep. Defaults to 1. Defaults to 1.
    """

    if products_data is None:
        products_data = import_data_from_agribalyse()

    for w in words_list:
        print(f"\n\n\n----- {w.upper()} -----")
        print(f"----- {clean_string(w)} -----\n")
        for d_name, d_func in dist_dict.items():
            print(d_name.upper())
            print(
                match_products(w, products_data=products_data, distance=d_func, n=n)[
                    ["name_prod", "clean_name_prod", "distance"]
                ]
            )
            print("\n")


#########################
### COMPUTE EMISSIONS ###
#########################


def compute_emissions(
    product_name: str,
    products_data: pd.DataFrame = None,
    distance: Callable = DIST["per"],
) -> pd.DataFrame:
    """Computes estimated emission figures for a given product name.

    Args:
        product_name (str): the name of the product.
        products_data (pd.DataFrame) : pandas DataFrame with the data related to a list of products.
            The column with the names of the products must be 'name_prod'. Defaults to None.
        distance (Callable, optional): method to compute the string distance. Defaults to
            Levenshtein's distance.
    """

    if products_data is None:
        products_data = import_data_from_agribalyse()

    results = match_products(
        product_name, products_data=products_data, distance=distance, n=1
    ).rename(columns={"distance": "uncertainty"})

    results["agribalyse_match"] = results["name_prod"]
    results["name_prod"] = product_name
    return results
