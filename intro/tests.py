from otree.api import Currency as c, currency_range, expect, Bot, Submission
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Consent, dict(consent_given=True)
        yield Submission(Instructions, check_html=False)
