# scrapper marmiton
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from conversions_to_grams import CONVERSIONS_TO_GRAMS


###########################
### CONVERSION TO FLOAT ###
###########################


def convert_to_float(frac_str : str) -> float:
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
        return whole - frac if whole < 0 else whole + frac ### dans quel cas a-t-on whole < 0 ?


options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")
options.add_argument("--user-agent=Mozilla/5.0")

try:
    driver = webdriver.Chrome("chromedriver", options=options)
except WebDriverException:
    driver = webdriver.Chrome("/path/to/chromedriver", options=options)


# Fonction de traitement de texte de sortie


def create_dictionnaire_recette_ingredients(a):
    recette = {}
    for i in range(len(a) // 2):
        key = a[2 * i + 1]
        key = key.split("de ")[-1].lower()
        value = a[2 * i].split("  ")
        value = value[0].split()
        value[0] = convert_to_float(value[0])
        if len(value) == 1:
            value.append("")
        # Pour les unités type fruits/légumes
        if key.find("+") == True:
            key = key.split("+")[0]
        # Ici utiliser les algo de distance pour savoir si value[1] est ds notre base ou pas
        if key.find("(") == True:
            key = key.split("(")[0]
        if key.find(" "):
            key = key.split(" ")[0]
        if value[1] in CONVERSIONS_TO_GRAMS:
            value[0] = CONVERSIONS_TO_GRAMS[value[1]] * value[0]
            value[1] = "g"
        if value[1] == "":
            if key in CONVERSIONS_TO_GRAMS:
                value[0] = CONVERSIONS_TO_GRAMS[key] * value[0]
                value[1] = "g"
        if value[1] == "g":
            recette[key] = value
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
            dico_infos_recette[
                "recette_ingredients"
            ] = create_dictionnaire_recette_ingredients(Recette.text.split("\n"))
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