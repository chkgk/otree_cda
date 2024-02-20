from otree.api import Currency as c, currency_range, expect, Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Part3Announcement
        yield CRT7, {
            "crt7_jerry": 29,
            "crt7_machines": 5,
            "crt7_stocks": 2,
            "crt7_ball": 0.05,
            "crt7_lake": 47,
            "crt7_pig": 20,
            "crt7_barrels": 3  # wrong answer
        }
        assert self.player.crt7_score == 6/7