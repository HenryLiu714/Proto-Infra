import requests

from alpaca.trading.client import TradingClient

from Alert import send_alert
from Types import *

class ExecutionHandler(object):
    def __init__(self, trading_client: TradingClient):
        self.trading_client = trading_client

    def execute_order(self, order: Order):
        pass