from otree.api import *

from kocher_cda.models import Subsession, Group, Player, Order, Trade
from kocher_cda.pages import BaseTradingWaitPage, BaseTradingPage, BaseTradingSummaryPage
from kocher_cda.functions import create_market_session

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'cda_practice'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10


# FUNCTIONS
def creating_session(subsession):
    create_market_session(subsession)


# PAGES
class TradingWaitPage(BaseTradingWaitPage):
    pass


class Trading(BaseTradingPage):
    pass


class TradingSummary(BaseTradingSummaryPage):
    pass


page_sequence = [TradingWaitPage, Trading, TradingSummary]
