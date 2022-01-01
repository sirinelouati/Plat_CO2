from src.food2emissions import (
    import_data_from_agribalyse,
    match_products,
    compare_methods,
    compute_emissions,
)

from src.scrapper_marmiton import marmiton_scrapper

print(marmiton_scrapper("tarte aux pommes", 2))


if __name__ == "__main__":

    """products_data = import_data_from_agribalyse()

    print(
        "Here are the 5 products from Agribalyse that are closest to 'Sucre blanc'.\n"
    )

    print(match_products("Sucre blanc", products_data=products_data, n=5))

    print("\n\n\n")

    print("Here are the figures related to the CO2 emissions of 'Sucre blanc'.\n")

    print(compute_emissions("Sucre blanc", products_data=products_data))

    print("\n\n\n")

    print(
        "Here are the matching results using 3 different methods to compute string distances, tested on 3 differents products : 'Sucre blanc', 'steach haché', 'lait de soja'.\n"
    )

    compare_methods(
        ["Sucre blanc", "steak haché", "lait de soja"],
        products_data=products_data,
        n=3,
    )"""
