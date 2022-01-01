import warnings

warnings.filterwarnings("ignore")  # TO FIX


#######################
### STRING CLEANING ###
#######################

from unidecode import unidecode
from re import sub


def clean_string(s: str) -> str:
    """Cleans up the string s to enhance the matching.
    Stemming and lemmatization are not implemented because they would reduce the matching
    performance.

    Args:
        s (str): string to clean up

    Returns:
        str: string cleaned up
    """

    s = unidecode(s)  # remove accents
    s = s.lower()  # force lowercase
    s = sub("[^a-z ]", " ", s)  # only keeps letters and spaces
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