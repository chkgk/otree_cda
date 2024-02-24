from otree.api import *

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
