from math import ceil
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from src.conversions import CONVERSIONS_TO_GRAMS, CONVERSIONS_TO_ML
from src.utils import DIST, clean_string
import time
from tqdm import tqdm
from typing import Callable, Dict


###########################
### CONVERSION TO FLOAT ###
###########################


def convert_to_float(frac_str: str) -> float:
    """returns the float corresponding to a fractionnal expression given as a string

    Args:
        frac_str (str): fractionnal expression (ex : 1/2, 3⁄4, 5 1/2, ...)

    Returns:
        float: value of the expression
    """

    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split("⁄")
        try:
            leading, num = num.split(" ")
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole + frac


#############################
### STANDARD OUTPUT MAKER ###
#############################


def find_closest_match(product_name: str, distance: Callable = DIST["per"]) -> str:
    """returns the closest product to 'product_name' in the conversion list (conversions.py)

    Args:
        product_name (str): product missing from the conversion list
        distance (Callable, optional): function that computes a distance between two strings. Its value is 0
            for a perfect match, 1 in the worst case. Defaults to Levenshtein's distance.
    Returns:
        str: the name of the best matching product in the conversion list
    """

    return min(
        [convertible for convertible in CONVERSIONS_TO_GRAMS.keys()],
        key=lambda x: distance(x, product_name),
    )


def make_output(content: str, verbose: bool = False) -> Dict:
    """makes a standard dictionnary from the raw text corresponding to a given recipe

    Args:
        content (str): raw text extracted from Marmiton's html page
        verbose (bool): True to display any html list of ingredients that cannot be interpreted

    Returns:
        Dict: dictionnary matching each ingredient to its corresponding mass in grams
    """

    content = content.split("\n")
    recette = {}
    missing_convertible = (
        []
    )  # stores the ingredients that are missing from our conversion list

    missing_quantity = []  # stores the indices where no quantity has been provided
    for i in range(ceil(len(content) / 2)):
        if not re.match(r"\d", content[2 * i - len(missing_quantity)]):
            missing_quantity.append(2 * i - len(missing_quantity))

    for i, j in enumerate(missing_quantity):
        content.insert(i + j, "1")  # fills the missing quantities with 1

    if len(content) % 2 == 1:
        if verbose:
            print(
                "\r"
                + f"[INFO] Cannot interpret the following list of ingredients : {content}\n"
            )
        return None  # cannot process the list of ingredients

    for i in range(len(content) // 2):
        key = content[2 * i + 1].lstrip().rstrip()
        if key.startswith("de "):
            key = key[3:]
        elif key.startswith("d'"):
            key = key[2:]
        if (
            "+" in key or "(" in key
        ):  # for ingredients such as butter (eg: "100 g (+ 10 g pour beurrer le moule)")
            key = key.split(" +")[0].split(" (")[0]

        value = content[2 * i].split("  ")
        raw_quantity = re.match(
            r"(?P<quantity>[\d /⁄.,]*)? ?(?P<unit>.*)?", value[0]
        ).groupdict()  # handles pathologic cases such as "3 1/2 boîtes moyennes"
        quantity = raw_quantity["quantity"]
        unit = raw_quantity["unit"]

        if not quantity:  # if no quantity is specified, we set its value at 1
            quantity = "1"

        quantity = convert_to_float(quantity)
        unit = clean_string(unit)
        product = clean_string(key)

        if unit in CONVERSIONS_TO_GRAMS:  # eg : "3 pincées de sel"
            quantity = CONVERSIONS_TO_GRAMS[unit] * quantity
            unit = "g"
        elif unit in CONVERSIONS_TO_ML:  # eg : "5 cl d'huile"
            if product in CONVERSIONS_TO_GRAMS:
                quantity = (
                    CONVERSIONS_TO_GRAMS[product] * CONVERSIONS_TO_ML[unit]
                ) * quantity
                unit = "g"
            else:  # eg : "5 cl d'huile d'olive de la marque Lorem Ipsum"
                closest_match = find_closest_match(product)
                quantity = (
                    CONVERSIONS_TO_GRAMS[closest_match]
                    * CONVERSIONS_TO_ML[unit]
                    * quantity
                )
                unit = "g"
                missing_convertible.append((key, closest_match))
        elif unit == "":  # eg : "5 pommes"
            if product in CONVERSIONS_TO_GRAMS:
                quantity = CONVERSIONS_TO_GRAMS[product] * quantity
                unit = "g"
            else:  # eg : "5 pommes de la variété Lorem Ipsum"
                closest_match = find_closest_match(product)
                quantity = CONVERSIONS_TO_GRAMS[closest_match] * quantity
                unit = "g"
                missing_convertible.append((key, closest_match))
        if unit == "g":  # eg : "10 g de sucre"
            recette[key] = quantity
        else:  # for unhandled cases such as "1 boîte de compote"
            print(
                "\r"
                + f"[INFO] Cannot convert an ingredient to grams : ({key}, {raw_quantity}).                             \n"
            )
            return None

    return (recette, missing_convertible)


#############################
### SCRAPPER FOR MARMITON ###
#############################


def marmiton_scrapper(recipe_name: str, n: int) -> Dict:
    """returns the data corresponding the the n first recipes Marmiton proposes for 'recipe_name'

    Args:
        recipe_name (str): name of a recipe (eg : "gâteau au chocolat")
        n (int): number of results to return

    Returns:
        Dict: the key refers to a single recipe, the value is a Dict containing relevant data
    """

    options = (
        webdriver.ChromeOptions()
    )  # these options are mandatory when using Google Colaboratory
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")

    try:
        driver = webdriver.Chrome(
            "/usr/lib/chromium-browser/chromedriver", options=options
        )  # for Linux or MacOS
    except WebDriverException:
        driver = webdriver.Chrome(
            "chromedriver", options=options
        )  # for Google Collaboratory or Windows

    print("\nStarting to scrap Marmiton... (please wait about 10 seconds)\n")

    recipes = {}
    driver.get("https://www.marmiton.org/")
    time.sleep(3)  # waiting for cookies to pop-up

    try:  # handling cookies pop-up
        Cookie = driver.find_element(By.ID, "didomi-notice-agree-button")
        Cookie.click()
        time.sleep(1)  # let's be respectful !
    except NoSuchElementException:
        pass

    print("Cookies handled !\n")

    search_bar = driver.find_element(By.TAG_NAME, "input")
    search_bar.send_keys(recipe_name)
    search_bar.send_keys(Keys.RETURN)
    time.sleep(1)

    print(f"Collecting results for '{recipe_name}'...\n")

    links_list = (
        [  # list of the links of all the recipes from the first page of results
            x.get_attribute("href") for x in driver.find_elements(By.XPATH, "//main//a")
        ]
    )

    missing_convertible = []

    i = 0
    for i in tqdm(
        range(min(n, len(links_list))), ncols=100
    ):  # tqdm handles the loading bar

        url = links_list[i]

        try:
            driver.get(url)
            time.sleep(1)
            recipe = driver.find_element(
                By.XPATH,
                "/html/body/div[2]/div[3]/main/div/div/div[1]/div[1]/div[7]/div[2]/div[2]/div/div/div/div[2]",
            )
            nb_people = driver.find_element(
                By.XPATH,
                "/html/body/div[2]/div[3]/main/div/div/div[1]/div[1]/div[7]/div[2]/div[1]/div[1]/div/span[1]",
            )

            nb_comments = driver.find_element(
                By.XPATH,
                "/html/body/div[2]/div[3]/main/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/a/span",
            )
            mark = driver.find_element(
                By.XPATH,
                "/html/body/div[2]/div[3]/main/div/div/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/span",
            )
            nb_comments_int = int(nb_comments.text.split()[0])
            mark_float = float(mark.text[: mark.text.find("/")])

            # Create standard output
            recipe_dict = {}
            current_output = make_output(recipe.text)
            if current_output is None:  # conversion aborted
                n += 1
                continue
            recipe_dict["ingredients"], new_missing_convertible = current_output
            recipe_dict["nb_people"] = int(nb_people.text.split("\n")[0])
            recipe_dict["nb_comments"] = nb_comments_int
            recipe_dict["mark"] = mark_float
            recipe_dict["url"] = url
            recipes[driver.find_element(By.TAG_NAME, "h1").text] = recipe_dict

            missing_convertible += new_missing_convertible

        except NoSuchElementException:
            pass

        i += 1

    if missing_convertible:
        print(
            "\nThe following ingredients were missing from the conversion list (conversions.py) :"
        )
        for (missing, matching) in missing_convertible:
            print(f"    ---> '{missing}' was remplaced by '{matching}'")
        print(
            "\nThese ingredients shall be added to the conversion list to be properly processed in the future.\n"
        )

    driver.close()
    print("Marmiton's data is extracted !\n")

    return recipes
