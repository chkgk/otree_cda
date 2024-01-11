from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)


author = 'Felix Holzmeister. Adapted by Christian König-Kersting in 2024.'

doc = """
Advanced Progressive Matrices (Raven 1976).
"""


# ******************************************************************************************************************** #
# *** CLASS CONSTANTS
# ******************************************************************************************************************** #
class Constants(BaseConstants):
    name_in_url = 'apm'
    players_per_group = None

    gto_seconds = 600

    # list of correct answers
    # ----------------------------------------------------------------------------------------------------------------
    correct = [
        5,  # 01
        1,  # 02
        7,  # 03
        4,  # 04
        3,  # 05
        1,  # 06
        6,  # 07
        1,  # 08
        8,  # 09
        4,  # 10
        5,  # 11
        6,  # 12
        2,  # 13
        1,  # 14
        2,  # 15
        4,  # 16
        6,  # 17
        7,  # 18
        3,  # 19
        8,  # 20
        8,  # 21
        7,  # 22
        6,  # 23
        3,  # 24
        7,  # 25
        2,  # 26
        7,  # 27
        5,  # 28
        6,  # 29
        5,  # 30
        4,  # 31
        8,  # 32
        5,  # 33
        1,  # 34
        3,  # 35
        2   # 36
    ]

    # dynamically determine list of all images
    # ----------------------------------------------------------------------------------------------------------------
    # images = [str(j)+'.png' for j in range(1,37)]
    images = [f"{j}.png" for j in range(1,37)]
    indices = [j[:-4] for j in images]

    # only keep odd-numbered items
    # ----------------------------------------------------------------------------------------------------------------
    images = images[::2]
    correct = correct[::2]

    # set number of rounds
    # ----------------------------------------------------------------------------------------------------------------
    num_rounds = len(images)


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

    choice = models.IntegerField()
    correct = models.IntegerField()
    score = models.IntegerField()

    # verify whether choice has been correct
    # ----------------------------------------------------------------------------------------------------------------
    def verify_if_correct(self):
        if self.choice == self.correct:
            self.score = 1
        else:
            self.score = 0
