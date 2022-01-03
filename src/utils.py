import warnings

warnings.filterwarnings("ignore")  # TO FIX


#######################
### STRING CLEANING ###
#######################

from unidecode import unidecode
from re import sub


def clean_string(s: str) -> str:
    """Cleans up the string s to enhance the matching.
    Lemmatization is not implemented because it would reduce the matching
    performance.

    Args:
        s (str): string to clean up

    Returns:
        str: string cleaned up
    """

    s = unidecode(s)  # remove accents
    s = s.lower()  # force lowercase
    s = sub("[^a-z ]", " ", s)  # only keeps letters and spaces
    s = s.lstrip().rstrip()  # remove leading and ending spaces
    from nltk.stem.snowball import FrenchStemmer

    s = " ".join(FrenchStemmer().stem(s) for s in s.split())  # stemming

    return s


###############################
### STRING DISTANCE METHODS ###
###############################

# The normalized methods are stored in the dictionnary 'DIST'.
# Their value is 0 for a perfect match, 1 in the worst case.

DIST = {}


# Gestalt Pattern Matching (gpm)
# Initial range of values : from 0 (worst case) to 1 (perfect match).

from difflib import SequenceMatcher

DIST["gpm"] = lambda a, b: 1 - SequenceMatcher(None, a, b).ratio()


# FuzzyWuzzy's partial ratio (fwz)
# Initial range of values : from 0 (worst case) to 100 (perfect partial match).

from fuzzywuzzy.fuzz import partial_ratio

DIST["fwz"] = lambda a, b: 1 - partial_ratio(a, b) / 100


# Levenshtein distance (lev)
# Initial range of values : from 0 (perfect match) to the length of the longest string (worst case).

from nltk import edit_distance

DIST["lev"] = lambda a, b: edit_distance(a, b) / max(len(a), len(b))


# Personalized distance (per)
# This distance is specially designed to compare ingredients


def personalized_distance(a: str, b: str) -> float:

    if a == b:
        return 0.0

    la, lb = len(a), len(b)
    if la > lb:  # let a be the shortest string
        la, lb, a, b = lb, la, b, a

    if (
        ("beurr" in a) and not ("cacao" in a) and ("beurr de cacao" in b)
    ):  # frequent pathologic case
        return 1.0

    if b.startswith(a):
        return 0.2 - 0.2 * la / lb
    a_split = a.split()
    if b.startswith(a_split[0]):
        common_start = a_split[0]
        i = 1
        while i < len(a_split) and b.startswith(common_start):
            common_start += a_split[i]
            i += 1
        return 0.4 - 0.2 * len(common_start) / la
    elif a in b:
        return 0.6 - 0.2 * b.find(a) / lb
    elif a_split[0] in b:
        return 0.6 + 0.2 * DIST["gpm"](a, b)
    else:
        return 0.8 + 0.2 * DIST["lev"](a, b)


DIST["per"] = personalized_distance
