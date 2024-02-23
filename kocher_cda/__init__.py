from otree.api import *
from otree.settings import DEBUG
from uuid import uuid4
import time

from .market_functions import create_market_session, handle_order

doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'kocher_cda'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 10


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


# FUNCTIONS
def creating_session(subsession):
    create_market_session(subsession)


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
        to_add = {'player_id': replacement_order.player.id_in_group, 'uuid': replacement_order.uuid, 'side': replacement_order.side, 'price': replacement_order.price, 'quantity': replacement_order.quantity, "kind": replacement_order.kind, "created": replacement_order.created}
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
    def get_timeout_seconds(player):
        return player.session.config["trading_seconds"]

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
    def get_timeout_seconds(player):
        return player.session.config["trading_summary_seconds"]

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


page_sequence = [TradingWaitPage, Trading, TradingSummary]
