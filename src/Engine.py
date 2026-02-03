from pydantic import BaseModel
from dotenv import load_dotenv
import os

from alpaca.trading.client import TradingClient

from Strategy import *
from Portfolio import *
from ExecutionHandler import ExecutionHandler
from Context import *
from Events import *
from Types import *

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")

class Engine(EventSink):
    def __init__(self):
        self.strategy: Strategy = None
        self.portfolio: Portfolio = None

        self.event_queue: list[Event] = []

        self.trading_client: TradingClient = TradingClient(ALPACA_API_KEY, ALPACA_SECRET, paper=True)
        self.execution_handler: ExecutionHandler = ExecutionHandler(self.trading_client)

    def publish(self, event: Event):
        self.event_queue.append(event)

    def set_strategy(self, strategy: Strategy):
        self.strategy = strategy
        self.strategy.set_context(Context(event_sink=self))

    def set_portfolio(self, portfolio: Portfolio):
        self.portfolio = portfolio
        self.portfolio.set_context(Context(event_sink=self))