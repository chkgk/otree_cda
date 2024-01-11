from otree.api import Currency as c, currency_range
from . import models
from ._builtin import Page, WaitPage
from .models import Constants



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

    # form model and form fields
    # ----------------------------------------------------------------------------------------------------------------
    form_model = models.Player
    form_fields = ['choice']

    # variables for template
    # ----------------------------------------------------------------------------------------------------------------
    def vars_for_template(self):

        # specify info for task progress
        task = self.session.config['app_sequence'].index('egt')
        task_total = self.player.participant.vars.get('task_total', 1)
        task_progress = task / task_total * 100

        # specify info for progress bar
        total = len(Constants.images)
        page = self.subsession.round_number
        progress = page / total * 100

        item_set = list(
            zip(
                Constants.choices[page - 1],
                Constants.synonyms[page - 1],
                Constants.examples[page - 1]
            )
        )

        # return variables
        return {
            'task':          task,
            'task_total':    task_total,
            'task_progress': task_progress,
            'page':          page,
            'total':         total,
            'progress':      progress,
            'img':           'egt/img/' + Constants.images[page - 1],
            'images':        Constants.images,
            'set':           item_set
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
    Practice,
    Decision
]
