from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Part4Announcement
        yield Demographics1
        # yield Demographics2
        yield Payments