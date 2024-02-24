from otree.api import *

from kocher_cda.ex_models import Subsession, Group, Player, Order, Trade
from kocher_cda.pages import BaseTradingWaitPage, BaseTradingPage, BaseTradingResultsWaitPage, BaseTradingSummaryPage
from kocher_cda.functions import market_create_session, market_custom_export

doc = """
Your app description
"""

class C(BaseConstants):
    NAME_IN_URL = 'cda_rep2'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10


# FUNCTIONS
def creating_session(subsession: Subsession):
    return market_create_session(subsession, repetition=2)


def custom_export(players):
    return market_custom_export(players, repetition=2)


# PAGES
class TradingWaitPage(BaseTradingWaitPage):
    pass


class Trading(BaseTradingPage):
    pass


class TradingResultsWaitPage(BaseTradingWaitPage):
    pass


class TradingSummary(BaseTradingSummaryPage):
    pass


page_sequence = [TradingWaitPage, Trading, TradingResultsWaitPage, TradingSummary]
