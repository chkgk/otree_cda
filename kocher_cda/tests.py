from otree.api import Currency as c, currency_range, expect, Bot
from . import Trading, TradingSummary


class PlayerBot(Bot):
    def play_round(self):
        yield Trading
        yield TradingSummary
