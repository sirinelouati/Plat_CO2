# scrapper marmiton
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from src.utils import clean_string
import time
from typing import Dict

from conversions_to_grams import CONVERSIONS_TO_GRAMS


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


options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")
options.add_argument("--user-agent=Mozilla/5.0")

try:
    driver = webdriver.Chrome("chromedriver", options=options)
except WebDriverException:
    driver = webdriver.Chrome("/path/to/chromedriver", options=options)


#############################
### STANDARD OUTPUT MAKER ###
#############################


def make_output(content: str) -> Dict:
    """makes a standard dictionnary from the raw text corresponding to a given recipe

    Args:
        content (str): raw text extracted from Marmiton's html page

    Returns:
        Dict: {"recette_ingredients": Dict, "nombre_personne": int, "note_fiabilite_recette": float, "url_recette": str}
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
            key = key.split("+").split("(")[0]

        value = content[2 * i].split("  ")
        value = value[0].split()
        value[0] = convert_to_float(value[0])
        if len(value) == 1:  # for ingredients without unit (eg : 3 apples)
            value.append("")

        clean_value_1 = clean_string(value[1])
        if clean_value_1 in CONVERSIONS_TO_GRAMS:
            value[0] = CONVERSIONS_TO_GRAMS[clean_value_1] * value[0]
            value[1] = "g"
        elif clean_value_1 == "":
            clean_key = clean_string(key)
            if clean_key in CONVERSIONS_TO_GRAMS:
                value[0] = CONVERSIONS_TO_GRAMS[clean_key] * value[0]
                value[1] = "g"
        if value[1] == "g":
            recette[key] = value
        else:
            print(
                f"[INFO] A new item has been detected : {value[1]} must be added to the conversion list."
            )

    return recette


# Le Scrapper Marmiton


def marmitonscrapper(root, nbre_recettes):
    recettes = {}
    # Le driver va chercher sur le site de marmiton
    driver.get("https://www.marmiton.org/")
    time.sleep(3)
    try:
        Cookie = driver.find_element(By.ID, "didomi-notice-agree-button")
        time.sleep(3)
        Cookie.click()
        time.sleep(3)
    except NoSuchElementException:
        pass

    with open("page.html", "w") as f:
        f.write(driver.page_source)
    time.sleep(3)
    search_bar = driver.find_element(By.TAG_NAME, "input")
    search_bar.send_keys(root)
    search_bar.send_keys(Keys.RETURN)
    time.sleep(3)
    links_list = [
        x.get_attribute("href") for x in driver.find_elements(By.XPATH, "//main//a")
    ]
    cpt = 0
    while cpt < min(nbre_recettes, len(links_list)):
        url = links_list[cpt]
        try:
            # Ouverture de la recette correspondante
            # pas sur utilité de la commande du dessous "link = driver.get(url)""
            link = driver.get(url)
            time.sleep(1)
            time.sleep(1)
            Recette = driver.find_element(
                By.XPATH,
                "/html/body/div[2]/div[3]/main/div/div/div[1]/div[1]/div[7]/div[2]/div[2]/div/div/div/div[2]",
            )
            time.sleep(1)
            # extraction nbre de personne
            nbre_personne = driver.find_element(
                By.XPATH,
                "/html/body/div[2]/div[3]/main/div/div/div[1]/div[1]/div[7]/div[2]/div[1]/div[1]/div/span[1]",
            )
            time.sleep(1)
            # Extraction nbre de commentaires et la note de la recette
            nbre_commentaires = driver.find_element(
                By.XPATH,
                "/html/body/div[2]/div[3]/main/div/div/div[1]/div[1]/div[2]/div[2]/div[2]/a/span",
            )
            time.sleep(1)
            note_recette = driver.find_element(
                By.XPATH,
                "/html/body/div[2]/div[3]/main/div/div/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/span",
            )
            # Transformation note et nombre de commentaires en valeur numérique
            nbre_commentaires_int = int(nbre_commentaires.text.split()[0])
            note_recette_float = float(note_recette.text[: note_recette.text.find("/")])
            # Construction indicateur fiabilité entre 0 et 1 (note/commentaires)
            ##Explication indicateur
            ##En général sur marmiton nbre de commentaires max sur une recette 1000
            ##Je considère à partir de 1000 commentaires la recette à la note maximale sur la partie commentaire (c'est pour cela je divise par 1000)
            ##Cette simplification va permettre de normaliser nos données
            ##Pondération 60% commentaires et 40% note
            ##Les notes  vont de 0 à 5
            note_fiabilite = 0.6 * min(nbre_commentaires_int / 1000, 1) + 0.4 * (
                note_recette_float / 5
            )
            # Traitement sortie création dictionnaire
            ##cpt numero de la recette mais amelioration possible créer variable recette_i avec i changeant##
            dico_infos_recette = {}
            dico_infos_recette["recette_ingredients"] = make_output(Recette.text)
            dico_infos_recette["nombre_personne"] = int(
                nbre_personne.text.split("\n")[0]
            )
            dico_infos_recette["note_fiabilite_recette"] = note_fiabilite
            dico_infos_recette["url_recette"] = url
            recettes["recette_" + str(cpt + 1)] = dico_infos_recette
        except NoSuchElementException:
            pass
        cpt = cpt + 1
    return recettes
