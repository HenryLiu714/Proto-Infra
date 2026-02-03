
from Types import *

class Portfolio(object):
    def __init__(self):
        self.context: Context = None

    def on_signal(self, signal: Signal):
        pass

    def on_fill(self, fill: Fill):
        pass

    def send_order(self, order: Order):
        pass

    def set_context(self, context: Context):
        self.context = context