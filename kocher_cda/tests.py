from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        if self.player.round_number == 1:
            yield Part2Announcement

        yield Trading
        yield TradingSummary
