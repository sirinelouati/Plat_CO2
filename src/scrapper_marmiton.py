from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from src.conversions import CONVERSIONS_TO_GRAMS, UNITS_VOLUME
from src.utils import clean_string
import time
from typing import Dict


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
        return (
            whole - frac if whole < 0 else whole + frac
        )  ### dans quel cas a-t-on whole < 0 ?


#############################
### STANDARD OUTPUT MAKER ###
#############################


def make_output(content: str) -> Dict:
    """makes a standard dictionnary from the raw text corresponding to a given recipe

    Args:
        content (str): raw text extracted from Marmiton's html page

    Returns:
        Dict: {"ingredients": Dict, "nb_people": int, "score": float, "url": str}
    """

    content = content.split("\n")
    recette = {}

    for i in range(len(content) // 2):
        key = content[2 * i + 1]
        if key.startswith("de "):
            key = key[3:]
        elif key.startswith("d'"):
            key = key[2:]
        if (
            "+" in key or "(" in key
        ):  # for ingredients such as butter (eg: "100 g (+ 10 g pour beurrer le moule)")
            key = key.split("+")[0].split("(")[0]

        value = content[2 * i].split("  ")
        value = value[0].split()
        if value == "":  # we decide to ignore the ingredients without a quantity
            pass
        else:
            value[0] = convert_to_float(value[0])
            if len(value) == 1:  # for ingredients without unit (eg : 3 apples)
                value.append("")

            clean_value_1 = clean_string(value[1])
            clean_key = clean_string(key)
            if clean_value_1 in CONVERSIONS_TO_GRAMS:
                value[0] = CONVERSIONS_TO_GRAMS[clean_value_1] * value[0]
                value[1] = "g"
            elif clean_value_1 in UNITS_VOLUME:
                if clean_key in CONVERSIONS_TO_GRAMS:
                    value[0] = (
                        CONVERSIONS_TO_GRAMS[clean_key] * UNITS_VOLUME[clean_value_1]
                    )
                    value[1] = "g"
                else:
                    raise Exception(
                        f"A new item has been detected : {key} must be added to the conversion list."
                    )
            elif clean_value_1 == "":
                if clean_key in CONVERSIONS_TO_GRAMS:
                    value[0] = CONVERSIONS_TO_GRAMS[clean_key] * value[0]
                    value[1] = "g"
                else:
                    raise Exception(
                        f"A new item has been detected : {key} must be added to the conversion list."
                    )
            if value[1] == "g":
                recette[key] = value
            else:
                raise Exception(
                    f"A new item has been detected : {value[1]} must be added to the conversion list."
                )

    return recette


#############################
### SCRAPPER FOR MARMITON ###
#############################


def marmiton_scrapper(recipe_name: str, n: int) -> Dict:
    """returns the data corresponding the the n first recipes Marmiton proposes for 'recipe_name'

    Args:
        recipe_name (str): name of a recipe (eg : "gâteau au chocolat")
        n (int): number of results to return

    Returns:
        Dict: the key refers to a single recipe, the value is a Dict returned by the function 'make_output'
    """

    options = (
        webdriver.ChromeOptions()
    )  # these options are mandatory when using Google Colaboratory
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")

    try:
        driver = webdriver.Chrome(
            "chromedriver", options=options
        )  # for Google Collaboratory or Windows
    except WebDriverException:
        driver = webdriver.Chrome(
            "/path/to/chromedriver", options=options
        )  # for Linux or MacOS

    recipes = {}
    driver.get("https://www.marmiton.org/")
    time.sleep(3)  # waiting for cookies to pop-up

    try:  # handling cookies pop-up
        Cookie = driver.find_element(By.ID, "didomi-notice-agree-button")
        Cookie.click()
        time.sleep(1)  # let's be respectful !
    except NoSuchElementException:
        pass

    search_bar = driver.find_element(By.TAG_NAME, "input")
    search_bar.send_keys(recipe_name)
    search_bar.send_keys(Keys.RETURN)
    time.sleep(1)

    links_list = (
        [  # list of the links of all the recipes from the first page of results
            x.get_attribute("href") for x in driver.find_elements(By.XPATH, "//main//a")
        ]
    )

    i = 0
    while i < min(n, len(links_list)):

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

            ## Compute the recipe's score
            # The score take into account both the number of comments and the average mark.
            # On Marmiton, the recipes usually get at most 1000 comments.
            # On Marmiton, the marks go from 0 (bad recipe) to 5 (good recipe).
            # We decided to give a weight of 60% to the number of comments and 40% to the mark.
            # Our aggregated score goes from 0 (bad recipe) to 1 (good recipe).

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
            note_fiabilite = 0.6 * min(nb_comments_int / 1000, 1) + 0.4 * (
                mark_float / 5
            )

            # Create standard output
            recipe_dict = {}
            recipe_dict["ingredients"] = make_output(recipe.text)
            recipe_dict["nb_people"] = int(nb_people.text.split("\n")[0])
            recipe_dict["score"] = note_fiabilite
            recipe_dict["url"] = url
            recipes["recette_" + str(i + 1)] = recipe_dict
        except NoSuchElementException:
            pass
        i = i + 1

    return recipes
