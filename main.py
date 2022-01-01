from src.food2emissions import (
    import_data_from_agribalyse,
    match_products,
    compare_methods,
    compute_emissions,
)
from src.dummy import dummy_output1
from src.aggregate import match_all_ingredients, compute_recipes_figures
from src.scrapper_marmiton import marmiton_scrapper
from src.utils import DIST


def demo_food2emissions():
    products_data = import_data_from_agribalyse()
    print(
        "Here are the 5 products from Agribalyse that are closest to 'Sucre blanc'.\n"
    )
    print(match_products("Sucre blanc", products_data=products_data, n=5))
    print("\n\n\n")
    print("Here are the figures related to the CO2 emissions of 'Sucre blanc'.\n")
    print(compute_emissions("Sucre blanc", products_data=products_data))
    print("\n\n\n")
    print(
        "Here are the matching results using 4 different methods to compute string distances, tested on 3 differents products : 'Sucre blanc', 'steach haché', 'lait de soja'.\n"
    )
    compare_methods(
        ["Sucre blanc", "steak haché", "lait de soja"],
        products_data=products_data,
        n=3,
    )


def demo_aggregate_1():

    print(
        match_all_ingredients(
            dummy_output1,
        )
    )


def demo_aggregate_2():
    emissions, uncertainties = compute_recipes_figures(
        marmiton_scrapper("gâteau au chocolat", 6)
    )
    print(
        """\n
    #################
    ### EMISSIONS ###
    #################
    """
    )
    print(emissions)
    print(
        """\n
    #####################
    ### UNCERTAINTIES ###
    #####################
    """
    )
    print(uncertainties)


def demo_scrapper():
    # print(marmiton_scrapper("tarte aux pommes", 4))
    print(marmiton_scrapper("gâteau au chocolat", 4))


if __name__ == "__main__":

    demo_aggregate_2()
