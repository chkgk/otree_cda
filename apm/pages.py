from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants
from otree.settings import DEBUG, LANGUAGE_CODE
from common.pages import TranslatedPage, LANGUAGE_MAP

import time


# ******************************************************************************************************************** #
# *** PAGE INSTRUCTIONS *** #
# ******************************************************************************************************************** #
class Instructions(TranslatedPage):

    # only display instruction in round 1
    # ----------------------------------------------------------------------------------------------------------------
    def is_displayed(self):
        return self.subsession.round_number == 1

    def before_next_page(player):
        player.participant.vars["apm_overall_timeout"] = time.time() + Constants.gto_seconds


# ******************************************************************************************************************** #
# *** PAGE DECISION *** #
# ******************************************************************************************************************** #
class Decision(TranslatedPage):
    form_model = models.Player
    form_fields = ['choice']

    def get_timeout_seconds(self):
        return self.player.participant.vars["apm_overall_timeout"] - time.time()

    def is_displayed(self):
        return self.get_timeout_seconds() > 3

    def vars_for_template(self):
        # specify info for progress bar
        total = Constants.num_rounds
        page = self.subsession.round_number
        progress = page / total * 100

        # specify info for image
        idx = Constants.images[page - 1][:-4]

        return {
            'page':          page,
            'total':         total,
            'progress':      progress,
            'img':           "apm/img/matrices/" + Constants.images[page - 1],
            'index':         Constants.images[page - 1][:-4],
            'images':        [(i, f"apm/img/answers/{idx}_{i}.png") for i in "12345678"]
        }

    def before_next_page(self):
        self.player.verify_if_correct()


# ******************************************************************************************************************** #
# *** PAGE SEQUENCE *** #
# ******************************************************************************************************************** #
page_sequence = [
    Instructions,
    Decision
]
