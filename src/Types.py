from enum import Enum
from pydantic import BaseModel, Field

class EventType(str, Enum):
    MARKET = "MARKET"
    SIGNAL = "SIGNAL"
    ORDER = "ORDER"
    FILL = "FILL"

class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"

class Bar(BaseModel):
    symbol: str
    timestamp: float
    open_price: float = Field(..., alias='open')
    high: float
    low: float
    close: float
    volume: float

class Fill(BaseModel):
    symbol: str
    quantity: float
    fill_price: float
    commission: float

class Order(BaseModel):
    order_id: str | None = None # Alpaca order ID
    order_type: OrderType
    symbol: str
    quantity: float
    direction: Direction
    price: float | None = None

class Signal(BaseModel):
    strategy_id: str
    symbol: str
    value: float