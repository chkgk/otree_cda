from otree.api import *
from otree import settings
from kocher_cda.models import *
from kocher_cda.functions import handle_order, cancel_order
import time


class BaseTradingWaitPage(WaitPage):
    # wait_for_all_groups = True

    def is_displayed(player):
        return player.round_number <= player.session.config["num_rounds"]

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


class BaseTradingPage(Page):
    def get_template_name(self):
        return f"kocher_cda/Trading_{settings.LANGUAGE_CODE}.html"

    def get_timeout_seconds(player):
        return player.session.config["trading_seconds"]

    def is_displayed(player):
        return player.round_number <= player.session.config["num_rounds"]

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
            "max_rounds": player.session.config["num_rounds"],
            "LANGUAGE_CODE": settings.LANGUAGE_CODE
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


class BaseTradingSummaryPage(Page):
    def get_template_name(self):
        return f"kocher_cda/TradingSummary_{settings.LANGUAGE_CODE}.html"

    def is_displayed(player):
        return player.round_number <= player.session.config["num_rounds"]

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
            "max_rounds": player.session.config["num_rounds"],
            "LANGUAGE_CODE": settings.LANGUAGE_CODE
        }

    def js_vars(player):
        average_prices = list()
        for g in player.group.in_all_rounds():
            average_prices.append([g.round_number, g.average_price])

        return {
            "average_prices": average_prices
        }
