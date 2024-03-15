from otree.api import Currency as c, currency_range, expect, Bot, Submission
from . import *
import time 

class PlayerBot(Bot):
    def play_round(self):
        yield Page1
        # yield Movie
        if self.player.id_in_group == 1:
            time.sleep(20)
