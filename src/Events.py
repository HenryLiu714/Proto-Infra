from pydantic import BaseModel
from Types import *

class Event(BaseModel):
    event_type: str
    timestamp: float

class MarketEvent(Event):
    event_type: str = "MARKET"
    bars: dict[str, Bar]

class SignalEvent(Event):
    event_type: str = "SIGNAL"
    signal: Signal

class OrderEvent(Event):
    event_type: str = "ORDER"
    order: Order

class FillEvent(Event):
    event_type: str = "FILL"
    fill: Fill