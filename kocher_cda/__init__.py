from otree.api import *
from otree.settings import DEBUG
from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func
from uuid import uuid4
import random
import json

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
    TRADING_SUMMARY_SECONDS = 30

    CASH_AND_ASSET_ENDOWMENTS = {
        "high": (3000, 20),
        "low": (1000, 60)
    }


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):  # market level
    dividend = models.IntegerField()
    closing_price = models.IntegerField()


class Player(BasePlayer):
    assets = models.IntegerField()
    cash = models.IntegerField()
    dividend_payment = models.IntegerField()
    next_cash = models.IntegerField()

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

    def as_dict(self):
        return dict(
            player_id=self.player.id_in_group,
            group_id=self.group.id_in_subsession,
            uuid=self.uuid,
            round=self.round,
            is_bid=self.is_bid,
            price=self.price,
            quantity=self.quantity,
            deleted=self.deleted,
            created=str(self.created)
        )

class Trade(ExtraModel):
    order = models.Link(Order)
    quantity = models.IntegerField()
    price = models.FloatField()
    type = models.StringField()
    created = Column(DateTime(timezone=True), server_default=func.now())

# FUNCTIONS
def vars_for_admin_report(subsession):
    import json
    return {
        "orders": json.dumps([order.as_dict() for order in Order.filter()])
    }

def creating_session(subsession):
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


def handle_order(player, is_bid, data):
    order = Order.create(player=player, group=player.group, round=player.round_number, uuid=str(uuid4()), is_bid=is_bid, price=data["price"], quantity=data["quantity"])
    typ = "bid_placed" if is_bid else "ask_placed"
    data.update({"uuid": order.uuid, "player_id": order.player.id_in_group})
    return {0: {"type": typ, "data": data}}


def handle_market_order(player, is_bid, data):
    orders = Order.filter(group=player.group, round=player.round_number, is_bid=(not is_bid), deleted=False)

    orders = sorted(orders, key=lambda x: x.price, reverse=(not is_bid))

    quantity = data["quantity"]
    to_fill = int(quantity)
    trades = list()
    to_remove = list()
    to_update = list()

    # this needs to track volume to check if budget is exceeded
    for order in orders:
        if to_fill >= order.quantity:
            to_fill -= order.quantity
            trades.append({"object": order, "uuid": order.uuid, "initiated_by": player.id_in_group, "affected": order.player.id_in_group, "price": order.price, "quantity": order.quantity})
            to_remove.append(order)
            order.deleted = True
        else:  # to fill < order.quantity
            order.quantity -= to_fill
            trades.append({"object": order, "uuid": order.uuid, "initiated_by": player.id_in_group, "affected": order.player.id_in_group, "price": order.price, "quantity": to_fill})
            to_update.append(order)
            to_fill = 0

        if to_fill == 0:
            break

    affected_players = {trade["affected"]: {} for trade in trades}
    affected_players.update({player.id_in_group: {}})
    for trade in trades:
        q = int(trade["quantity"])
        p = int(trade["price"])
        player.cash -= p * q
        player.assets += q
        other_player = player.group.get_player_by_id(trade["affected"])
        other_player.cash += p * q
        other_player.assets -= q

        Trade.create(order=trade['object'], type="market", quantity=q, price=p)

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
class Part2Announcement(Page):
    def is_displayed(player):
        return player.round_number == 1


class TradingWaitPage(WaitPage):
    # wait_for_all_groups = True

    def after_all_players_arrive(group: Group):
        if group.round_number == 1:
            return

        for player in group.get_players():
            prev_player = player.in_round(group.round_number - 1)
            player.cash = prev_player.next_cash
            player.assets = prev_player.assets

class Trading(Page):
    # timeout_seconds = C.TRADING_SECONDS
    
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

        asks = [{"price": order.price, "quantity": order.quantity, "uuid": order.uuid, "player_id": order.player.id_in_group} for order in Order.filter(group=player.group, is_bid=False, deleted=False)]

        bids = [{"price": order.price, "quantity": order.quantity, "uuid": order.uuid, "player_id": order.player.id_in_group} for order in Order.filter(group=player.group, is_bid=True, deleted=False)]

        return {
            "player_id": player.id_in_group,
            "asks": sorted(asks, key=lambda x: x["price"]),
            "bids": sorted(bids, key=lambda x: x["price"], reverse=True),
            "cash": player.cash,
            "assets": player.assets,
        }

    def before_next_page(player, timeout_happened):

        # ToDo: actually implement last trade price
        last_trade_price = random.randint(20, 100)
        print("last trade price not implemented")

        if player.group.field_maybe_none('closing_price') is None:
            player.group.closing_price = last_trade_price

        player.dividend_payment = player.assets * player.group.dividend
        player.next_cash = player.cash + player.dividend_payment

class TradingSummary(Page):
    # timeout_seconds = C.TRADING_SUMMARY_SECONDS
    
    def vars_for_template(player):
        history = []
        for p in player.in_all_rounds():
            g = p.group
            if p.round_number <= player.round_number:
                history.append({
                    "round": p.round_number, 
                    "cash": p.cash, 
                    "assets": p.assets,
                    "closing_price": g.closing_price,
                    "dividend": g.dividend,
                    "dividend_sum": p.dividend_payment,
                    "total": p.cash + p.dividend_payment
                })
        return {
            "history": history,
        }

    def js_vars(player):
        closing_prices = list()
        for g in player.group.in_all_rounds():
            closing_prices.append([g.round_number, g.closing_price])

        # ToDo: Remove demo data
        if closing_prices:
            closing_prices = [
                [1, 10],
                [2, 20],
                [3, 22],
                [4, 20],
                [5, 30],
                [6, 40],
                [7, 30],
                [8, 25],
                [9, 10],
                [10, 5]
            ]

        return {
            "closing_prices": closing_prices
        }


page_sequence = [Part2Announcement, TradingWaitPage, Trading, TradingSummary]
