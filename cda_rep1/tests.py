from otree.api import Currency as c, currency_range, expect, Bot, Submission
from . import Trading, TradingSummary


class PlayerBot(Bot):
    def play_round(self):
        yield Submission(Trading, check_html=False)
        yield Submission(TradingSummary, check_html=False)