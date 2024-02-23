from otree.api import *
import random
from otree.settings import DEBUG


def check_market_session_config(config):
    if not config.get("num_rounds", None):
        raise Exception("num_rounds not set in session config")
    if not config.get("trading_seconds", None):
        raise Exception("trading_seconds not set in session config")
    if not config.get("trading_summary_seconds", None):
        raise Exception("trading_summary_seconds not set in session config")
    if not config.get("dividend_high", None):
        raise Exception("dividend_high not set in session config")
    if not config.get("dividend_low", None):
        raise Exception("dividend_low not set in session config")
    if not config.get("endowment_high_cash", None):
        raise Exception("endowment_high_cash not set in session config")
    if not config.get("endowment_low_cash", None):
        raise Exception("endowment_low_cash not set in session config")


def create_market_session(subsession):
    sc = subsession.session.config
    check_market_session_config(sc)

    num_traders = len(subsession.get_players())
    if DEBUG:
        traders_per_market = int(num_traders / 2)
        num_markets = 2
    else:
        if num_traders % 16 != 0 and num_traders % 20 != 0:
            raise Exception("Need a multiple of 16 or 20 traders")

        traders_per_market = 10 if num_traders % 20 == 0 else 8
        num_markets = int(num_traders / traders_per_market)

    # set group matrix
    if subsession.round_number == 1:
        group_matrix = []
        for market in range(num_markets):
            group_matrix.append([market * traders_per_market + i + 1 for i in range(traders_per_market)])

        subsession.set_group_matrix(group_matrix)
    else:
        subsession.group_like_round(1)

    # prepare dividend sequence dict
    if subsession.round_number == 1:
        subsession.session.vars["dividend_sequences"] = dict()

    for group in subsession.get_groups():
        # set sequence of high and low dividends
        if subsession.round_number == 1:
            dividend_sequence = [sc["dividend_high"] for i in range(int(sc["num_rounds"] / 2))] + [sc["dividend_low"] for i in
                                                                                              range(
                                                                                                  int(sc["num_rounds"] / 2))]
            random.shuffle(dividend_sequence)
            subsession.session.vars["dividend_sequences"][group.id_in_subsession] = dividend_sequence
        else:
            dividend_sequence = subsession.session.vars.get("dividend_sequences")[group.id_in_subsession]

        # set dividend
        group.dividend = dividend_sequence[subsession.round_number - 1]

        # set cash and assets
        for player in group.get_players():
            # first round endowments
            if subsession.round_number == 1:
                if player.id_in_group <= traders_per_market / 2:
                    player.cash, player.assets = sc["endowment_high_cash"]
                else:
                    player.cash, player.assets = sc["endowment_low_cash"]
                player.available_cash = player.cash
                player.available_assets = player.assets