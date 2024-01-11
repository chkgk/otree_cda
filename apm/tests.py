from otree.api import Currency as c, currency_range
from . import pages
from ._builtin import Bot
from .models import Constants
import random


class PlayerBot(Bot):

    def play_round(self):

        # define page as round_number
        page = self.subsession.round_number

        # ------------------------------------------------------------------------------------------------------------ #
        # submit instructions page
        # ------------------------------------------------------------------------------------------------------------ #
        if page == 1:
            yield (pages.Instructions)

        # ------------------------------------------------------------------------------------------------------------ #
        # make decisions
        # ------------------------------------------------------------------------------------------------------------ #
        yield (pages.Decision, {'choice': random.randint(1,8)})
