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


######################
### DEMONSTRATIONS ###
######################


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


def demo_aggregate():

    print(
        match_all_ingredients(
            dummy_output1,
        )
    )


def demo_interface(
    emissions=dummy_emissions,
    uncertainties=dummy_uncertainties,
    ingredients=dummy_ingredients,
    cross=dummy_cross,
):
    _, ingredients_data, cross_data = preprocess_data(
        emissions, uncertainties, ingredients, cross
    )
    compare_recipes(cross_data)
    compare_ingredients(ingredients_data)


########################
### DUMMY GENERATORS ###
########################


def dummy_scrapper(recipe="gâteau au chocolat", nmax = 10):

    output1 = marmiton_scrapper(recipe, nmax)
    print(
        """\n
    ###############
    ### OUTPUT1 ###
    ###############
    """
    )
    print(output1.to_dict())
    return output1


def dummy_aggregate(output1=dummy_output1):
    emissions, uncertainties, ingredients, cross_emissions = compute_recipes_figures(
        output1
    )
    print(
        """\n
    #################
    ### EMISSIONS ###
    #################
    """
    )
    print(emissions.to_dict())
    print(
        """\n
    #####################
    ### UNCERTAINTIES ###
    #####################
    """
    )
    print(uncertainties.to_dict())
    print(
        """\n
    ###################
    ### INGREDIENTS ###
    ###################
    """
    )
    print(ingredients.to_dict())
    print(
        """\n
    #######################
    ### CROSS EMISSIONS ###
    #######################
    """
    )
    print(cross_emissions.to_dict())


def generate_all_dummy(recipe="gâteau au chocolat", nmax=10):

    dummy_aggregate(dummy_scrapper(recipe, nmax))


################
### PIPELINE ###
################


def main(recipe="gâteau au chocolat", nmax=10):

    scrapper_result = marmiton_scrapper(recipe, nmax)

    emissions, uncertainties, ingredients, cross_emissions = compute_recipes_figures(
        scrapper_result
    )

    _, ingredients_data, cross_data = preprocess_data(
        emissions, uncertainties, ingredients, cross_emissions
    )

    compare_recipes(cross_data)
    compare_ingredients(ingredients_data)


if __name__ == "__main__":

    generate_all_dummy()
