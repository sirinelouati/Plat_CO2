from src.food2emissions import (
    import_data_from_agribalyse,
    match_products,
    compare_methods,
    compute_emissions,
)
from src.dummy import (
    dummy_output1,
    dummy_emissions,
    dummy_uncertainties,
    dummy_ingredients,
    dummy_cross,
)
from src.aggregate import match_all_ingredients, compute_recipes_figures
from src.interface import compare_ingredients, compare_recipes, preprocess_data
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
    emissions, uncertainties, ingredients, cross_emissions = compute_recipes_figures(
        dummy_output1
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
    print(
        """\n
    ###################
    ### INGREDIENTS ###
    ###################
    """
    )
    print(ingredients)
    print(
        """\n
    #######################
    ### CROSS EMISSIONS ###
    #######################
    """
    )
    print(cross_emissions.to_dict())


def demo_scrapper():
    # print(marmiton_scrapper("tarte aux pommes", 4))
    print(marmiton_scrapper("gâteau au chocolat", 4))


def demo_interface():
    _, b, c = preprocess_data(
        dummy_emissions, dummy_uncertainties, dummy_ingredients, dummy_cross
    )
    compare_recipes(c)
    compare_ingredients(b)


def demo():

    _, b, c = preprocess_data(
        *compute_recipes_figures(marmiton_scrapper("crumble aux pommes", 8))
    )

    compare_recipes(c)
    compare_ingredients(b)


if __name__ == "__main__":

    demo()
