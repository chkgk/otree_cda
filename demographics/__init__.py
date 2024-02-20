from otree.api import *
from otree.settings import DEBUG, LANGUAGE_CODE
from common.pages import TranslatedPage, LANGUAGE_MAP

doc = """
Your app description
"""

def _(s):
    LANGUAGE_MAP["de"] = {
        
    }
    if LANGUAGE_CODE in LANGUAGE_MAP.keys():
        return LANGUAGE_MAP[LANGUAGE_CODE][s]
    return s


class C(BaseConstants):
    NAME_IN_URL = 'demographics'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class Part4Announcement(TranslatedPage):
    pass


class Demographics1(TranslatedPage):
    pass


class Payments(TranslatedPage):
    pass


page_sequence = [
    Part4Announcement,
    Demographics1,
    # Demographics2,
    Payments
]
