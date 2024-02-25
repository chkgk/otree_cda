from otree.api import *

from kocher_cda import *
doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'cda_practice'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    num_rounds = models.IntegerField()
    repetition = models.IntegerField()
    practice = models.BooleanField()


class Group(BaseGroup):  # market level
    dividend = models.IntegerField()
    closing_price = models.FloatField()
    average_price = models.FloatField()
    starting_timestamp = models.IntegerField()


class Player(BasePlayer):
    cash = models.IntegerField()
    assets = models.IntegerField()
    available_cash = models.IntegerField()
    available_assets = models.IntegerField()

    dividend_payment = models.IntegerField()
    next_cash = models.IntegerField()


class Order(ExtraModel):
    uuid = models.StringField()
    repetition= models.IntegerField()
    group = models.Link(Group)
    round = models.IntegerField()
    player = models.Link(Player)
    kind = models.StringField()
    side = models.StringField()
    quantity = models.IntegerField()
    price = models.IntegerField()
    filled = models.BooleanField(default=False)
    is_replacement = models.BooleanField(default=False)
    replaced_by = models.StringField()
    deleted = models.BooleanField(default=False)
    created = models.IntegerField()


class Trade(ExtraModel):
    uuid = models.StringField()
    repetition= models.IntegerField()
    group = models.Link(Group)
    round = models.IntegerField()
    ask = models.Link(Order)
    bid = models.Link(Order)
    quantity = models.IntegerField()
    price = models.IntegerField()
    created = models.IntegerField()

# FUNCTIONS
# for some reason, this function is not called.
# I have no idea why
# Here is a potential work-around:
# in the kocher_cda app, the creating session is executed. We can track where we are if specifically told in the session config. 
# if that info is not available, we can check if we have played the practice round or the first repetition already. in this case, we know where we are.
# ugly but might work
def creating_session(subsession: Subsession):
    print("print yay")
    return market_create_session(subsession, repetition=0)


def custom_export(players):
    return market_custom_export(players, repetition=0)

