from otree.api import *
from otree.settings import DEBUG, LANGUAGE_CODE
from common.pages import TranslatedPage, LANGUAGE_MAP

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'cda_practice'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class PracticeAnnouncement(Page):
    timeout_seconds = 10


class PracticePeriod(Page):
    pass


class PracticeSummary(Page):
    pass


class Part1Announcement(TranslatedPage):
    pass


class Part1Waitpage(WaitPage):
    wait_for_all_groups = True

    def is_displayed(player):
        return not DEBUG


page_sequence = [PracticeAnnouncement, PracticePeriod, PracticeSummary, Part1Announcement, Part1Waitpage]
