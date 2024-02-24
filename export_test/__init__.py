from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'export_test'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass

class Offer(ExtraModel):
    group = models.Link(Group)
    quantity = models.IntegerField(min=0, max=100)
    price = models.CurrencyField(min=0, max=100)

class Trade(ExtraModel):
    group = models.Link(Group)
    info = models.IntegerField(min=0, max=100)

# FUNCTIONS
def creating_session(subsession: Subsession):
    import random
    for group in subsession.get_groups():
        for i in range(10):
            Offer.create(group=group, quantity=random.randint(0, 100), price=random.randint(0, 100))
        for i in range(5):
            Trade.create(group=group, info=random.randint(0, 100))


def custom_export(players):
    import random
    # we generate a long random string to separate the tables add to avoide collisions with data entered by participants
    random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))

    # first row contains the string at which to split tables and the names of the tables in the correct order
    yield [random_string, "Offer", "Trade"]
    # then we yield the table rows for the first table
    yield ['group_id', 'quantity', 'price']
    for o in Offer.filter():
        yield o.group.id_in_subsession, o.quantity, o.price

    # to indicate the start of the next table, we yield the string again
    yield [random_string]
    # followed by data for the next table
    yield ['group_id', 'info']
    for t in Trade.filter():
        yield t.group.id_in_subsession, t.info

# PAGES
class MyPage(Page):
    pass


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage, Results]