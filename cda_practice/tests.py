from otree.api import Currency as c, currency_range, expect, Bot
from . import *
import random


class PlayerBot(Bot):
    def play_round(self):
        yield Submission(PracticeAnnouncement, check_html=False)
        yield PracticePeriod
        yield PracticeSummary
        yield Part1Announcement
