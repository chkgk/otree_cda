from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants

import time
# from otree.models_concrete import (PageTimeout, PageCompletion)
# from .gto_timeout import GTOPage



# ******************************************************************************************************************** #
# *** PAGE INSTRUCTIONS *** #
# ******************************************************************************************************************** #
class Instructions(Page):

    # only display instruction in round 1
    # ----------------------------------------------------------------------------------------------------------------
    def is_displayed(self):
        return self.subsession.round_number == 1


# ******************************************************************************************************************** #
# *** PAGE PRACTICE *** #
# ******************************************************************************************************************** #
class Practice(Page):

    # only display instruction in round 1
    # ----------------------------------------------------------------------------------------------------------------
    def is_displayed(self):
        return self.subsession.round_number == 1


# ******************************************************************************************************************** #
# *** PAGE DECISION *** #
# ******************************************************************************************************************** #
class Decision(Page):
    # GTOPage does not work anymore and is not easy to fix due to differen timeout handling in oTree5
    # need to implement a different way to have a timeout across multiple rounds

    general_timeout = True

    # form model and form fields
    # ----------------------------------------------------------------------------------------------------------------
    form_model = models.Player
    form_fields = ['choice']

    # variables for template
    # ----------------------------------------------------------------------------------------------------------------
    def vars_for_template(self):

        # specify info for task progress
        task = self.session.config['app_sequence'].index('apm')
        task_total = self.player.participant.vars.get('task_total', 1)
        task_progress = task / task_total * 100

        # specify info for progress bar
        total = Constants.num_rounds
        page = self.subsession.round_number
        progress = page / total * 100

        # specify info for image
        idx = Constants.images[page - 1][:-4]

        return {
            'task':          task,
            'task_total':    task_total,
            'task_progress': task_progress,
            'page':          page,
            'total':         total,
            'progress':      progress,
            'img':           "apm/img/matrices/" + Constants.images[page - 1],
            'index':         Constants.images[page - 1][:-4],
            'images':        [(i, f"apm/img/answers/{idx}_{i}.png") for i in "12345678"]
        }

    # verify whether choice has been correct
    # ----------------------------------------------------------------------------------------------------------------
    def before_next_page(self):
        self.player.verify_if_correct()


# ******************************************************************************************************************** #
# *** PAGE SEQUENCE *** #
# ******************************************************************************************************************** #
page_sequence = [
    Instructions,
    Decision
]
