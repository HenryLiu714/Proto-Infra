from src.Types import *
from src.Events import MarketEvent
from src.Context import *

class Strategy(object):
    def __init__(self, name):
        self.name = name
        self.context: Context = None

    def on_start(self):
        pass

    def on_update(self, event: MarketEvent):
        pass

    #!TODO: Implement
    def send_signal(self, signal: Signal):
        pass

    def set_context(self, context: Context):
        self.context = context