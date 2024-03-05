from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from otree.settings import LANGUAGE_CODE
from .data_en import CHOICES_EN, CORRECT_EN, PREVIEW_CHOICES_EN, PREVIEW_CORRECT_EN
from .data_de import CHOICES_DE, CORRECT_DE, PREVIEW_CHOICES_DE, PREVIEW_CORRECT_DE


author = 'Felix Holzmeister. Adapted by Christian König-Kersting in 2024.'

doc = """
Eye Gaze Test as proposed by Baron-Cohen et al (2001).
"""


# ******************************************************************************************************************** #
# *** CLASS CONSTANTS
# ******************************************************************************************************************** #
class Constants(BaseConstants):
    name_in_url = 'egt'
    players_per_group = None

    # list of lists of choices
    # ----------------------------------------------------------------------------------------------------------------
    choices = CHOICES_DE if LANGUAGE_CODE == 'de' else CHOICES_EN

    # list of correct answers
    # ----------------------------------------------------------------------------------------------------------------
    correct = CORRECT_DE if LANGUAGE_CODE == 'de' else CORRECT_EN

    preview_choices = PREVIEW_CHOICES_DE if LANGUAGE_CODE == 'de' else PREVIEW_CHOICES_EN
    preview_correct = PREVIEW_CORRECT_DE if LANGUAGE_CODE == 'de' else PREVIEW_CORRECT_EN

    # dynamically determine list of all images
    # ----------------------------------------------------------------------------------------------------------------
    images = [str(j)+'.png' for j in range(1, 37)]
    # commenting this out. Corgnet et al did all 36 in 10 minutes.

    # only keep odd-numbered items
    # ----------------------------------------------------------------------------------------------------------------
    # images = images[::2]
    # choices = choices[::2]
    # synonyms = synonyms[::2]
    # examples = examples[::2]
    # correct = correct[::2]

    # set number of rounds
    # ----------------------------------------------------------------------------------------------------------------
    num_rounds = len(images)

    gto_seconds = 600


# ******************************************************************************************************************** #
# *** CLASS SUBSESSION
# ******************************************************************************************************************** #
class Subsession(BaseSubsession):

    # set correct emotion
    # ----------------------------------------------------------------------------------------------------------------
    def creating_session(self):
        for p in self.get_players():
            p.correct = Constants.correct[self.round_number - 1]


# ******************************************************************************************************************** #
# *** CLASS GROUP
# ******************************************************************************************************************** #
class Group(BaseGroup):
    pass


# ******************************************************************************************************************** #
# *** CLASS PLAYER
# ******************************************************************************************************************** #
class Player(BasePlayer):

    choice = models.CharField()
    correct = models.CharField()
    score = models.IntegerField()

    # verify whether choice has been correct
    # ----------------------------------------------------------------------------------------------------------------
    def verify_if_correct(self):
        if self.choice == self.correct:
            self.score = 1
        else:
            self.score = 0
