from otree.api import *
from otree.settings import DEBUG
from uuid import uuid4
import random
import time

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


def generate_uuid():
    return str(uuid4())


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

    def as_dict(self):
        return dict(
            uuid=self.uuid,
            group_id=self.group.id_in_subsession,
            round=self.round,
            player_id=self.player.id_in_group,
            kind=self.kind,
            side=self.side,
            quantity=self.quantity,
            price=self.price,
            filled=self.filled,
            replaced_by=self.replaced_by,
            deleted=self.deleted,
            created=self.created
        )


class Trade(ExtraModel):
    group = models.Link(Group)
    round = models.IntegerField()
    ask = models.Link(Order)
    bid = models.Link(Order)
    quantity = models.IntegerField()
    price = models.FloatField()
    created = models.IntegerField()


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
                player.available_cash = player.cash
                player.available_assets = player.assets

def handle_order(player, data):
    if data["kind"] == "limit":
        return handle_limit_order(player, data)

    if data["kind"] == "market":
        return handle_market_order(player, data)

    print(data)


def handle_limit_order(player, data):
    order = Order.create(
        uuid=str(uuid4()),
        group=player.group,
        round=player.round_number,
        player=player,
        kind="limit",
        side=data["side"],
        quantity=data["quantity"],
        price=data["price"],
        created=int(time.time()) - player.group.starting_timestamp
    )

    if data["side"] == "ask":
        player.available_assets -= data["quantity"]
    else:  # bid
        player.available_cash -= data["quantity"] * data["price"]

    data.update({"uuid": order.uuid, "player_id": order.player.id_in_group})

    payload = {
        "order_data": data,
        "affected_players": {
            player.id_in_group: {
                "cash": player.cash,
                "assets": player.assets,
                "available_cash": player.available_cash,
                "available_assets": player.available_assets,
                "purchase_history_add": {},
                "sale_history_add": {}
            }
        }
    }

    return {0: {"type": 'order', "payload": payload}}


def handle_market_order(player, data):
    self_side = data["side"]
    other_side = "ask" if self_side == "bid" else "bid"

    # get open orders
    orders = Order.filter(
        group=player.group,
        round=player.round_number,
        kind="limit",
        side=other_side,
        filled=False,
        deleted=False
    )

    if not orders:
        # ToDo: Implement no orders found
        return

    # get the best one
    orders = sorted(orders, key=lambda x: x.price, reverse=(self_side == "ask"))
    best_order = orders[0]

    # limit the quantity to the best order quantity
    ordered_quantity = int(data["quantity"])
    actual_quantity = min(ordered_quantity, best_order.quantity)

    # create the market order
    market_order = Order.create(
        uuid=str(uuid4()),
        group=player.group,
        round=player.round_number,
        player=player,
        kind="market",
        side=self_side,
        quantity=actual_quantity,
        price=best_order.price,
        created=int(time.time()) - player.group.starting_timestamp
    )

    # create the trade
    trade = Trade.create(
        group=player.group,
        round=player.round_number,
        ask=market_order if self_side == "ask" else best_order,
        bid=market_order if self_side == "bid" else best_order,
        quantity=actual_quantity,
        price=best_order.price,
        created=int(time.time()) - player.group.starting_timestamp
    )

    # update the original limit order
    best_order.filled = True
    to_add = {}
    if ordered_quantity < best_order.quantity:
        # create a replacement order
        remaining_quantity = best_order.quantity - ordered_quantity
        replacement_order = Order.create(
            uuid=str(uuid4()),
            group=best_order.group,
            round=best_order.round,
            player=best_order.player,
            kind=best_order.kind,
            side=best_order.side,
            quantity=remaining_quantity,
            price=best_order.price,
            created=int(time.time()) - player.group.starting_timestamp
        )
        to_add = replacement_order.as_dict()
        best_order.replaced_by = replacement_order.uuid

    # get player objects
    ask_player = player if self_side == "ask" else best_order.player
    bid_player = player if self_side == "bid" else best_order.player

    # work out new cash and assets
    ask_player.cash += actual_quantity * best_order.price
    ask_player.assets -= actual_quantity

    bid_player.cash -= actual_quantity * best_order.price
    bid_player.assets += actual_quantity

    if self_side == "bid":
        bid_player.available_assets += actual_quantity
        bid_player.available_cash -= actual_quantity * best_order.price
        ask_player.available_cash += actual_quantity * best_order.price
        
    else:  # ask
        ask_player.available_assets -= actual_quantity
        ask_player.available_cash += actual_quantity * best_order.price
        bid_player.available_assets += actual_quantity


    affected_players = {
        ask_player.id_in_group: {
            "cash": ask_player.cash,
            "assets": ask_player.assets,
            "available_cash": ask_player.available_cash,
            "available_assets": ask_player.available_assets,
            "purchase_history_add": {},
            "sale_history_add": {
                "price": best_order.price,
                "quantity": actual_quantity
            }
        },
        bid_player.id_in_group: {
            "cash": bid_player.cash,
            "assets": bid_player.assets,
            "available_cash": bid_player.available_cash,
            "available_assets": bid_player.available_assets,
            "purchase_history_add": {
                "price": best_order.price,
                "quantity": actual_quantity
            },
            "sale_history_add": {}
        }
    }

    return {0: {
        "type": "market_order_filled",
        "payload": {
            "to_remove": best_order.uuid,
            "to_add": to_add,
            "affected_players": affected_players,
            "last_price": best_order.price,
        }
    }}


def cancel_order(player, data):
    orders = Order.filter(player=player, round=player.round_number, uuid=data["uuid"], deleted=False)
    for order in orders:
        order.deleted = True

        if order.side == "ask":
            player.available_assets += order.quantity
        else:  # bid
            player.available_cash += order.quantity * order.price

        payload = {
            "order_data": data,
            "affected_players": {
                player.id_in_group: {
                    "cash": player.cash,
                    "assets": player.assets,
                    "available_cash": player.available_cash,
                    "available_assets": player.available_assets,
                    "purchase_history_add": {},
                    "sale_history_add": {}
                }
            }
        }

        return {0: {"type": "order_cancelled", "payload": payload}}
    else:
        return {0: {"type": "order_cancel_failed", "payload": data}}


# PAGES
class Part2Announcement(Page):
    def is_displayed(player):
        return player.round_number == 1


class TradingWaitPage(WaitPage):
    # wait_for_all_groups = True

    def after_all_players_arrive(group: Group):
        group.starting_timestamp = int(time.time())
        if group.round_number == 1:
            return

        for player in group.get_players():
            prev_player = player.in_round(group.round_number - 1)
            player.cash = prev_player.next_cash
            player.assets = prev_player.assets
            player.available_cash = player.cash
            player.available_assets = player.assets

class Trading(Page):
    # timeout_seconds = C.TRADING_SECONDS
    # timeout_seconds = 120
    
    @staticmethod
    def live_method(player, req):
        print(req)
        if req["type"] == "order":
            return handle_order(player, req["payload"])

        if req["type"] == "cancel_order":
            return cancel_order(player, req["payload"])


    @staticmethod
    def js_vars(player):
        orders = Order.filter(group=player.group, round=player.round_number, kind="limit", filled=False, deleted=False)
        asks = [{"price": order.price, "quantity": order.quantity, "uuid": order.uuid, "player_id": order.player.id_in_group} for order in orders if order.side == "ask"]

        bids = [{"price": order.price, "quantity": order.quantity, "uuid": order.uuid, "player_id": order.player.id_in_group} for order in orders if order.side == "bid"]

        trades = Trade.filter(group=player.group, round=player.round_number)
        purchase_history = [{"price": t.price, "quantity": t.quantity, "created": t.created} for t in trades if t.bid.player == player]
        purchase_history.reverse()

        sale_history = [{"price": t.price, "quantity": t.quantity, "created": t.created} for t in trades if t.ask.player == player]
        sale_history.reverse()

        chart_series = [[t.created, t.price] for t in trades]

        return {
            "player_id": player.id_in_group,
            "asks": sorted(asks, key=lambda x: x["price"]),
            "bids": sorted(bids, key=lambda x: x["price"], reverse=True),
            "purchase_history": purchase_history,
            "sale_history": sale_history,
            "cash": player.cash,
            "assets": player.assets,
            "available_cash": player.available_cash,
            "available_assets": player.available_assets,
            "last_price": trades[-1].price if trades else None,
            "chart_series": chart_series,
            "market_start": player.group.starting_timestamp
        }

    def before_next_page(player, timeout_happened):
        if player.group.field_maybe_none('average_price') is None:
            trades = Trade.filter(group=player.group, round=player.round_number)
            if trades:
                player.group.average_price = sum([t.price for t in trades]) / len(trades)
                player.group.closing_price = trades[-1].price
            else:
                player.group.average_price = 0
                player.group.closing_price = 0

        player.dividend_payment = player.assets * player.group.dividend
        player.next_cash = player.cash + player.dividend_payment


class TradingSummary(Page):
    timeout_seconds = C.TRADING_SUMMARY_SECONDS

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
                    "average_price": g.average_price,
                    "dividend": g.dividend,
                    "dividend_sum": p.dividend_payment,
                    "total": p.cash + p.dividend_payment
                })
        return {
            "history": history,
        }

    def js_vars(player):
        average_prices = list()
        for g in player.group.in_all_rounds():
            average_prices.append([g.round_number, g.average_price])

        return {
            "average_prices": average_prices
        }


page_sequence = [Part2Announcement, TradingWaitPage, Trading, TradingSummary]
