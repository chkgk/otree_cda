from otree.settings import DEBUG

from uuid import uuid4
import random
import time

from kocher_cda.ex_models import *


def check_market_session_config(config):
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
        for player in group.get_players():
            # first round endowments
            if subsession.round_number == 1:
                if player.id_in_group <= traders_per_market / 2:
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
    for o in [order for order in Order.filter() if order.repetition == repetition]:
        yield o.uuid, o.group.session.code, o.repetition, o.group.id_in_subsession, o.round, o.player.id_in_group, o.kind, o.side, o.quantity, o.price, o.filled, o.is_replacement, o.replaced_by, o.deleted, o.created