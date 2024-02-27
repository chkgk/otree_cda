from otree.api import *
from otree.settings import DEBUG
from otree import settings

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


class Subsession(BaseSubsession):
    num_rounds = models.IntegerField()
    repetition = models.IntegerField()
    practice = models.BooleanField()


class Group(BaseGroup):  # market level
    dividend = models.IntegerField()
    closing_price = models.IntegerField()
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



#FUNCTIONS
def creating_session(subsession):
    sc_rep = subsession.session.config.get('repetition', None)
    if sc_rep is not None:
        subsession.session.vars["repetition"] = sc_rep
        repetition = sc_rep
    else:
        repetition = subsession.session.vars.get('repetition', 0)
    return market_create_session(subsession, repetition=repetition)


def check_market_session_config(config):
    if config.get("trading_seconds", None) is None:
        raise Exception("trading_seconds not set in session config")
    if config.get("trading_summary_seconds", None) is None:
        raise Exception("trading_summary_seconds not set in session config")
    if config.get("dividend_high", None) is None:
        raise Exception("dividend_high not set in session config")
    if config.get("dividend_low", None) is None:
        raise Exception("dividend_low not set in session config")
    if config.get("endowment_high_cash", None) is None:
        raise Exception("endowment_high_cash not set in session config")
    if config.get("endowment_low_cash", None) is None:
        raise Exception("endowment_low_cash not set in session config")


def market_create_session(subsession, repetition):
    sc = subsession.session.config
    check_market_session_config(sc)

    subsession.num_rounds = 1 if repetition == 0 else 10
    subsession.repetition = repetition
    subsession.practice = repetition == 0

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
            if subsession.num_rounds == 1:
                dividend_sequence = [sc["dividend_high"], 0, 0, 0, 0, 0, 0, 0, 0, 0]
            else:
                if subsession.num_rounds % 2 != 0:
                    raise Exception("num_rounds must be even")

                dividend_sequence = [sc["dividend_high"] for i in range(int(subsession.num_rounds / 2))] + [sc["dividend_low"] for i in range(int(subsession.num_rounds / 2))]
                random.shuffle(dividend_sequence)
                if len(dividend_sequence) < 10:
                    dividend_sequence += [0 for i in range(10 - len(dividend_sequence))]
            subsession.session.vars["dividend_sequences"][group.id_in_subsession] = dividend_sequence
        else:
            dividend_sequence = subsession.session.vars.get("dividend_sequences")[group.id_in_subsession]

        # set dividend
        group.dividend = dividend_sequence[subsession.round_number - 1]

        # set cash and assets
        # random sequence
        high_cash = [True for i in range(int(traders_per_market / 2))] + [False for i in range(int(traders_per_market / 2))]
        random.shuffle(high_cash)
        for player in group.get_players():
            # first round endowments
            if subsession.round_number == 1:
                if high_cash[player.id_in_group - 1]:
                    player.cash, player.assets = sc["endowment_high_cash"]
                else:
                    player.cash, player.assets = sc["endowment_low_cash"]

                player.available_cash = player.cash
                player.available_assets = player.assets


def handle_order(player, data):
    if data["kind"] == "limit":
        return handle_limit_order(player, data)

    if data["kind"] == "market":
        return handle_market_order(player, data)


def handle_limit_order(player, data):
    order = Order.create(
        uuid=str(uuid4()),
        repetition=player.subsession.repetition,
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
        repetition=player.subsession.repetition,
        group=player.group,
        round=player.round_number,
        player=player,
        kind="market",
        side=self_side,
        quantity=actual_quantity,
        price=best_order.price,
        filled=True,
        created=int(time.time()) - player.group.starting_timestamp
    )

    # create the trade
    trade = Trade.create(
        uuid=str(uuid4()),
        repetition=player.subsession.repetition,
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
            repetition=player.subsession.repetition,
            group=best_order.group,
            round=best_order.round,
            player=best_order.player,
            kind=best_order.kind,
            side=best_order.side,
            quantity=remaining_quantity,
            price=best_order.price,
            is_replacement=True,
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


def market_custom_export(players, repetition):
    # we generate a long random string to separate the tables add to avoide collisions with data entered by participants
    random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))

    # first row contains the string at which to split tables and the names of the tables in the correct order
    yield [random_string, f"Trade_{repetition}", f"Order_{repetition}"]
    # then we yield the table rows for the first table

    yield ['uuid', 'session_code', 'repetition', 'group_id', 'round_number', 'ask_uuid', 'bid_uuid', 'quantity', 'price', 'created']
    for t in [trade for trade in Trade.filter() if trade.repetition == repetition]:
        yield t.uuid, t.group.session.code, t.repetition, t.group.id_in_subsession, t.round, t.ask.uuid, t.bid.uuid, t.quantity, t.price, t.created


    # to indicate the start of the next table, we yield the string again
    yield [random_string]
    # followed by data for the next table
    yield ['uuid', 'session_code', 'repetition', 'group_id', 'round_number', 'player_id', 'kind', 'side', 'quantity', 'price', 'filled', 'is_replacement', 'replaced_by', 'deleted', 'created']


# PAGES


class BaseTradingWaitPage(WaitPage):
    # wait_for_all_groups = True

    def is_displayed(player):
        return player.round_number <= player.subsession.num_rounds

    def after_all_players_arrive(group):
        group.starting_timestamp = int(time.time())
        if group.round_number == 1:
            return

        for player in group.get_players():
            prev_player = player.in_round(group.round_number - 1)
            player.cash = prev_player.next_cash
            player.assets = prev_player.assets
            player.available_cash = player.cash
            player.available_assets = player.assets


class BaseTradingPage(Page):
    def get_template_name(self):
        return f"kocher_cda/Trading_{settings.LANGUAGE_CODE}.html"

    def get_timeout_seconds(player):
        return player.session.config["trading_seconds"]

    def is_displayed(player):
        return player.round_number <= player.subsession.num_rounds

    @staticmethod
    def live_method(player, req):
        if req["type"] == "order":
            return handle_order(player, req["payload"])

        if req["type"] == "cancel_order":
            return cancel_order(player, req["payload"])

    @staticmethod
    def js_vars(player):
        orders = Order.filter(group=player.group, round=player.round_number, kind="limit", filled=False, deleted=False)
        asks = [
            {"price": order.price, "quantity": order.quantity, "uuid": order.uuid,
             "player_id": order.player.id_in_group}
            for order in orders if order.side == "ask"]

        bids = [
            {"price": order.price, "quantity": order.quantity, "uuid": order.uuid,
             "player_id": order.player.id_in_group}
            for order in orders if order.side == "bid"]

        trades = Trade.filter(group=player.group, round=player.round_number)
        purchase_history = [{"price": t.price, "quantity": t.quantity, "created": t.created} for t in trades if
                            t.bid.player == player]
        purchase_history.reverse()

        sale_history = [{"price": t.price, "quantity": t.quantity, "created": t.created} for t in trades if
                        t.ask.player == player]
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
            "market_start": player.group.starting_timestamp,
        }

    def vars_for_template(player):
        return {
            "max_rounds": player.subsession.num_rounds,
            "LANGUAGE_CODE": settings.LANGUAGE_CODE
        }


class BaseTradingResultsWaitPage(WaitPage):
    def is_displayed(player):
        return player.round_number <= player.subsession.num_rounds

    def after_all_players_arrive(group: Group):
        trades = Trade.filter(group=group, round=group.round_number)
        if trades:
            group.average_price = sum([t.price for t in trades]) / len(trades)
            group.closing_price = trades[-1].price
        else:
            group.average_price = None
            group.closing_price = None

        # move on to next repetition
        if group.round_number == group.subsession.num_rounds:
            group.session.vars["repetition"] += 1

        for player in group.get_players():
            player.dividend_payment = player.assets * player.group.dividend
            player.next_cash = player.cash + player.dividend_payment

            if player.round_number == player.subsession.num_rounds and player.session.vars.get("pay_repetition", False) == player.subsession.repetition:
                player.payoff = player.next_cash


class BaseTradingSummaryPage(Page):
    def get_template_name(self):
        return f"kocher_cda/TradingSummary_{settings.LANGUAGE_CODE}.html"

    def is_displayed(player):
        return player.round_number <= player.subsession.num_rounds

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
                    "closing_price": g.field_maybe_none("closing_price"),
                    "average_price": g.field_maybe_none("average_price"),
                    "dividend": g.dividend,
                    "dividend_sum": p.dividend_payment,
                    "total": p.next_cash
                })
        return {
            "history": history,
            "max_rounds": player.subsession.num_rounds,
            "LANGUAGE_CODE": settings.LANGUAGE_CODE
        }

    def js_vars(player):
        average_prices = list()
        for g in player.group.in_all_rounds():
            average_prices.append([g.round_number, g.field_maybe_none("average_price")])

        return {
            "average_prices": average_prices
        }


class TradingWaitPage(BaseTradingWaitPage):
    pass


class Trading(BaseTradingPage):
    pass


class TradingResultsWaitPage(BaseTradingResultsWaitPage):
    pass


class TradingSummary(BaseTradingSummaryPage):
    pass


page_sequence = [TradingWaitPage, Trading, TradingResultsWaitPage, TradingSummary]
