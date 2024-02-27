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
    NAME_IN_URL = 'start_rep2'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class Rep2Announcement(TranslatedPage):
    pass



page_sequence = [Rep2Announcement]
