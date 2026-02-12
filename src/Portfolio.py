from src.Context import Context
from src.Types import *
from src.Events import OrderEvent, MarketEvent

from src.Alert import send_alert
from datetime import timedelta
import pandas_ta_classic as ta

import math

from db.operations import create_position, update_position, get_open_positions
from db import get_universe_by_symbol, get_position_by_id
from db import models, get_latest_entries

class Portfolio(object):
    def __init__(self):
        self.context: Context = None
        self.open_positions: dict[str, Position] = {}
        self.max_positions = 5

        # Retrieve open positions from database and populate self.open_positions
        open_positions_from_db = get_open_positions()
        for position in open_positions_from_db:
            self.open_positions[position.symbol] = Position(symbol=position.symbol, position_id=str(position.id), side=position.side, quantity=position.quantity, entry_price=position.open_price)

    def create_exits(self, position: Position):

        # Exit conditions
        position_from_db = get_position_by_id(position.position_id)
        position_tags = position_from_db.tags

        # 1. Position has been open for more than 5 days
        today = self.context.current_time().date()
        if today >= datetime.strptime(position_tags["exit_date"], "%Y-%m-%d").date():
            order = Order(symbol=position.symbol, quantity=position.quantity, order_type=OrderType.MARKET, direction=Direction.SHORT if position.side == Direction.LONG else Direction.LONG, order_intent=OrderIntent.CLOSE)
            self.send_order(order)

        # 2. Position has gained >= 1 atr from entry price
        if position.side == Direction.LONG:
            if position_tags and "take_profit_price" in position_tags and position_tags["take_profit_price"] is not None:
                # Make exit limit order at take profit price
                order = Order(symbol=position.symbol, quantity=position.quantity, order_type=OrderType.LIMIT, direction=Direction.SHORT, order_intent=OrderIntent.CLOSE, price=float(position_tags["take_profit_price"]))

                send_alert(f"Creating take profit order for {position.symbol} at {position_tags['take_profit_price']}")
                self.send_order(order)

        elif position.side == Direction.SHORT:
            if position_tags and "take_profit_price" in position_tags and position_tags["take_profit_price"] is not None:
                # Make exit limit order at take profit price
                order = Order(symbol=position.symbol, quantity=position.quantity, order_type=OrderType.LIMIT, direction=Direction.LONG, order_intent=OrderIntent.CLOSE, price=float(position_tags["take_profit_price"]))
                self.send_order(order)

        # 3. Stop loss, <= 2 atr from entry price
        if position.side == Direction.LONG:
            if position_tags and "stop_loss_price" in position_tags and position_tags["stop_loss_price"] is not None:
                # Make exit market order
                order = Order(symbol=position.symbol, quantity=position.quantity, order_type=OrderType.MARKET, direction=Direction.SHORT, order_intent=OrderIntent.CLOSE, price=float(position_tags["stop_loss_price"]))

                send_alert(f"Creating stop loss order for {position.symbol} at {position_tags['stop_loss_price']}")
                self.send_order(order)
        elif position.side == Direction.SHORT:
            if position_tags and "stop_loss_price" in position_tags and position_tags["stop_loss_price"] is not None:
                # Make exit market order
                order = Order(symbol=position.symbol, quantity=position.quantity, order_type=OrderType.MARKET, direction=Direction.LONG, order_intent=OrderIntent.CLOSE, price=float(position_tags["stop_loss_price"]))
                self.send_order(order)

    def on_market_update(self, event: MarketEvent):
        for _, position in self.open_positions.items():
            self.create_exits(position)

        send_alert(f"Market update. Current open positions: {list(self.open_positions.keys())}")

    def on_signal(self, signal: Signal):
        if len(self.open_positions) >= self.max_positions:
            send_alert(f"Received signal for {signal.symbol} but max positions already open. Ignoring signal.")
            return

        if signal.strategy_id == "SniperStrategy":
            cash = self.context.get_cash()
            remaining_spots = self.max_positions - len(self.open_positions)
            cash_per_position = int(cash / remaining_spots)
            quantity = int(cash_per_position / signal.value)

            order = Order(symbol=signal.symbol, quantity=quantity, order_type=OrderType.LIMIT, direction=Direction.LONG, order_intent=OrderIntent.OPEN, price=round(signal.value, 2))
            self.send_order(order)

    def calculate_exit(self, position: Position) -> None:
        # Update tags: take_profit_price, stop_loss_price, exit date
        exit_date = position.entry_time.date() + timedelta(days=5)
        take_profit_price = None
        stop_loss_price = None

        table_name = get_universe_by_symbol(position.symbol)[-1].price_source_table
        latest_data = get_latest_entries(table_name=table_name, symbol=position.symbol, n=30)

        atr = ta.atr(latest_data["high"], latest_data["low"], latest_data["close"], length=14).iloc[-1]

        if position.side == Direction.LONG:
            take_profit_price = position.entry_price + atr
            stop_loss_price = position.entry_price - 2 * atr

        elif position.side == Direction.SHORT:
            take_profit_price = position.entry_price - atr
            stop_loss_price = position.entry_price + 2 * atr

        metadata = {
            "exit_date": exit_date.strftime("%Y-%m-%d"),
            "take_profit_price": round(take_profit_price, 2),
            "stop_loss_price": round(stop_loss_price, 2)
        }

        update_position(
            position_id=int(position.position_id),
            tags=metadata
        )

    def on_fill(self, fill: Fill):
        # Add the fill to the open positions if it is an opening fill, otherwise remove it from the open positions
        # TODO: Once we support partial fills, include fill.side as well
        if fill.symbol not in self.open_positions and fill.side == Direction.LONG:
            # Create database entry
            new_position: models.Position = create_position(
                symbol=fill.symbol,
                status='OPEN',
                side=fill.side,
                open_time=self.context.current_time(),
                open_price=fill.fill_price,
                quantity=fill.quantity
            )

            self.open_positions[fill.symbol] = Position(symbol=fill.symbol,
                                                        position_id=str(new_position.id),
                                                        side=fill.side,
                                                        quantity=fill.quantity,
                                                        entry_price=fill.fill_price,
                                                        entry_time=self.context.current_time())

            self.calculate_exit(self.open_positions[fill.symbol])
            self.create_exits(self.open_positions[fill.symbol])

        elif fill.side != self.open_positions[fill.symbol].side:
            # Update database entry
            # TODO: Add logic to handle partial fills (for now we are assuming all fills are complete fills)
            update_position(
                position_id=int(self.open_positions[fill.symbol].position_id),
                status='CLOSED',
                close_time=self.context.current_time(),
                close_price=fill.fill_price,
                commission_close=fill.commission
            )

            self.open_positions.pop(fill.symbol)

    def send_order(self, order: Order):
        order_event = OrderEvent(order=order)
        self.context.event_sink.publish(order_event)

    def set_context(self, context: Context):
        self.context = context