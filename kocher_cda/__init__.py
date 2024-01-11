from otree.api import *
from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func
from uuid import uuid4
import random

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'kocher_cda'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10

    DIVIDEND = {
        "high": 10,
        "low": 0
    }

    TRADING_SECONDS = 120

    CASH_AND_ASSET_ENDOWMENTS = {
        "high": (3000, 20),
        "low": (1000, 60)
    }


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):  # market level
    dividend = models.IntegerField()


class Player(BasePlayer):
    assets = models.IntegerField()
    cash = models.IntegerField()
    period_payoff = models.IntegerField()


def generate_uuid():
    return str(uuid4())


class Order(ExtraModel):
    player = models.Link(Player)
    group = models.Link(Group)
    uuid = models.StringField()
    round = models.IntegerField()
    is_bid = models.BooleanField()
    price = models.IntegerField()
    quantity = models.IntegerField()
    deleted = models.BooleanField(default=False)
    created = Column(DateTime(timezone=True), server_default=func.now())


# FUNCTIONS
def creating_session(subsession):
    num_traders = len(subsession.get_players())
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
            dividend_sequence = [C.DIVIDEND["high"] for i in range(int(C.NUM_ROUNDS/2))] + [C.DIVIDEND["low"] for i in range(int(C.NUM_ROUNDS/2))]
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
                    player.cash, player.assets = C.CASH_AND_ASSET_ENDOWMENTS["high"]
                else:
                    player.cash, player.assets = C.CASH_AND_ASSET_ENDOWMENTS["low"]
            # subsequent rounds start with prev. round results
            else:
                player.cash = player.in_round(subsession.round_number - 1).cash
                player.assets = player.in_round(subsession.round_number - 1).assets

def handle_order(player, is_bid, data):
    order = Order.create(player=player, group=player.group, round=player.round_number, uuid=str(uuid4()), is_bid=is_bid, price=data["price"], quantity=data["quantity"])
    typ = "bid_placed" if is_bid else "ask_placed"
    data.update({"uuid": order.uuid, "player_id": order.player.id_in_group})
    return {0: {"type": typ, "data": data}}


def handle_market_order(player, is_bid, data):
    orders = Order.filter(group=player.group, round=player.round_number, is_bid=(not is_bid), deleted=False)

    # should sort here!

    quantity = data["quantity"]
    to_fill = int(quantity)
    trades = list()
    to_remove = list()
    to_update = list()
    
    # needs to differentiate between bid and ask
    # this needs to track volume to check if budget is exceeded
    for order in orders:
        if to_fill >= order.quantity:
            to_fill -= order.quantity
            trades.append({"uuid": order.uuid, "initiated_by": player.id_in_group, "affected": order.player.id_in_group, "price": order.price, "quantity": order.quantity})
            to_remove.append(order)
            order.deleted = True
        else:  # to fill < order.quantity
            order.quantity -= to_fill
            trades.append({"uuid": order.uuid, "initiated_by": player.id_in_group, "affected": order.player.id_in_group, "price": order.price, "quantity": to_fill})
            to_update.append(order)
            to_fill = 0

        if to_fill == 0:
            break

    affected_players = {trade["affected"]: {} for trade in trades}
    affected_players.update({player.id_in_group: {}})
    for trade in trades:
        # needs to differentiate between bid and ask
        q = int(trade["quantity"])
        p = float(trade["price"])
        player.cash -= p * q
        player.assets += q
        other_player = player.group.get_player_by_id(trade["affected"])
        other_player.cash += p * q
        other_player.assets -= q

        affected_players[other_player.id_in_group] = {"cash": other_player.cash, "assets": other_player.assets}
    affected_players[player.id_in_group] = {"cash": player.cash, "assets": player.assets}

    return {0: {"type": "market_order_filled", "data": {"to_remove": [order.uuid for order in to_remove], "to_update": [{"uuid": order.uuid, "quantity": order.quantity} for order in to_update], "affected_players": affected_players}}}


def cancel_order(player, data):
    orders = Order.filter(player=player, uuid=data["uuid"], deleted=False)
    for order in orders:
        order.deleted = True
        data.update({"is_bid": order.is_bid})
        return {0: {"type": "order_cancelled", "data": data}}
    else:
        return {0: {"type": "order_cancel_failed", "data": data}}


# PAGES
class Trading(Page):
    @staticmethod
    def live_method(player, data):
        if data["type"] == "place_ask":
            return handle_order(player, False, data["data"])
        elif data["type"] == "place_bid":
            return handle_order(player, True, data["data"])
        elif data["type"] == "cancel_order":
            return cancel_order(player, data["data"])
        elif data["type"] == "place_market_ask":
            return handle_market_order(player, False, data["data"])
        elif data["type"] == "place_market_bid":
            return handle_market_order(player, True, data["data"])
        else:
            print(data)

    @staticmethod
    def js_vars(player):
        return {
            "player_id": player.id_in_group,
            "asks": [{"price": order.price, "quantity": order.quantity, "uuid": order.uuid, "player_id": order.player.id_in_group} for order in Order.filter(group=player.group, is_bid=False, deleted=False)],
            "bids": [{"price": order.price, "quantity": order.quantity, "uuid": order.uuid, "player_id": order.player.id_in_group} for order in Order.filter(group=player.group, is_bid=True, deleted=False)],
            "cash": player.cash,
            "assets": player.assets,
        }

    def before_next_page(player, timeout_happened):
        player.period_payoff = player.cash + player.assets * (C.HIGH_DIVIDEND if player.group.asset_high else C.LOW_DIVIDEND)


class Results(Page):
    pass


page_sequence = [Trading, Results]
