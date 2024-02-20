from otree.api import *


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


page_sequence = [PracticeAnnouncement, PracticePeriod, PracticeSummary]
