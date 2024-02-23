from otree.api import *


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):  # market level
    dividend = models.CurrencyField()
    closing_price = models.CurrencyField()
    average_price = models.CurrencyField()
    starting_timestamp = models.IntegerField()


class Player(BasePlayer):
    cash = models.CurrencyField()
    assets = models.IntegerField()
    available_cash = models.CurrencyField()
    available_assets = models.IntegerField()

    dividend_payment = models.CurrencyField()
    next_cash = models.CurrencyField()


class Order(ExtraModel):
    uuid = models.StringField()
    group = models.Link(Group)
    round = models.IntegerField()
    player = models.Link(Player)
    kind = models.StringField()
    side = models.StringField()
    quantity = models.IntegerField()
    price = models.IntegerField()
    filled = models.BooleanField(default=False)
    replaced_by = models.StringField()
    deleted = models.BooleanField(default=False)
    created = models.IntegerField()


class Trade(ExtraModel):
    group = models.Link(Group)
    round = models.IntegerField()
    ask = models.Link(Order)
    bid = models.Link(Order)
    quantity = models.IntegerField()
    price = models.FloatField()
    created = models.IntegerField()
