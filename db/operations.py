"""Database operations for trading tables."""

from typing import List, Optional, Dict, Any
from datetime import datetime

from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError

from .connection import get_db_session
from .models import Fill, Order, Position


# ===== FILL OPERATIONS =====

def create_fill(order_id: str, quantity: float, price: float, filled_at: Optional[datetime] = None) -> Optional[Fill]:
    """Create a new fill record."""
    try:
        with get_db_session() as session:
            fill = Fill(
                order_id=order_id,
                quantity=quantity,
                price=price,
                filled_at=filled_at
            )
            session.add(fill)
            session.flush()
            session.refresh(fill)
            # Access attributes before session closes
            fill_id = fill.fill_id
            session.expunge(fill)
            return fill
    except SQLAlchemyError as e:
        print(f"Error creating fill: {e}")
        return None


def get_fill_by_id(fill_id: int) -> Optional[Fill]:
    """Get a fill by its ID."""
    try:
        with get_db_session() as session:
            fill = session.query(Fill).filter(Fill.fill_id == fill_id).first()
            if fill:
                session.expunge(fill)
            return fill
    except SQLAlchemyError as e:
        print(f"Error getting fill: {e}")
        return None


def get_fills_by_order(order_id: str) -> List[Fill]:
    """Get all fills for a specific order."""
    try:
        with get_db_session() as session:
            fills = session.query(Fill).filter(Fill.order_id == order_id).all()
            for fill in fills:
                session.expunge(fill)
            return fills
    except SQLAlchemyError as e:
        print(f"Error getting fills: {e}")
        return []


def get_all_fills(limit: Optional[int] = None) -> List[Fill]:
    """Get all fills, optionally limited."""
    try:
        with get_db_session() as session:
            query = session.query(Fill).order_by(Fill.filled_at.desc())
            if limit:
                query = query.limit(limit)
            fills = query.all()
            for fill in fills:
                session.expunge(fill)
            return fills
    except SQLAlchemyError as e:
        print(f"Error getting fills: {e}")
        return []


# ===== ORDER OPERATIONS =====

def create_order(
    order_id: str,
    symbol: str,
    quantity_ordered: float,
    status: Optional[str] = "pending",
    quantity_filled: float = 0
) -> Optional[Order]:
    """Create a new order record."""
    try:
        with get_db_session() as session:
            order = Order(
                order_id=order_id,
                symbol=symbol,
                quantity_ordered=quantity_ordered,
                status=status,
                quantity_filled=quantity_filled
            )
            session.add(order)
            session.flush()
            session.refresh(order)
            # Access attributes before session closes
            _ = order.order_id
            session.expunge(order)
            return order
    except SQLAlchemyError as e:
        print(f"Error creating order: {e}")
        return None


def get_order_by_id(order_id: str) -> Optional[Order]:
    """Get an order by its ID."""
    try:
        with get_db_session() as session:
            order = session.query(Order).filter(Order.order_id == order_id).first()
            if order:
                session.expunge(order)
            return order
    except SQLAlchemyError as e:
        print(f"Error getting order: {e}")
        return None


def get_orders_by_symbol(symbol: str) -> List[Order]:
    """Get all orders for a specific symbol."""
    try:
        with get_db_session() as session:
            orders = session.query(Order).filter(Order.symbol == symbol).all()
            for order in orders:
                session.expunge(order)
            return orders
    except SQLAlchemyError as e:
        print(f"Error getting orders: {e}")
        return []


def get_orders_by_status(status: str) -> List[Order]:
    """Get all orders with a specific status."""
    try:
        with get_db_session() as session:
            orders = session.query(Order).filter(Order.status == status).all()
            for order in orders:
                session.expunge(order)
            return orders
    except SQLAlchemyError as e:
        print(f"Error getting orders: {e}")
        return []


def update_order_status(order_id: str, status: str, quantity_filled: Optional[float] = None) -> bool:
    """Update order status and optionally quantity filled."""
    try:
        with get_db_session() as session:
            update_data = {"status": status}
            if quantity_filled is not None:
                update_data["quantity_filled"] = quantity_filled

            session.query(Order).filter(Order.order_id == order_id).update(update_data)
            return True
    except SQLAlchemyError as e:
        print(f"Error updating order: {e}")
        return False


def get_all_orders(limit: Optional[int] = None) -> List[Order]:
    """Get all orders, optionally limited."""
    try:
        with get_db_session() as session:
            query = session.query(Order).order_by(Order.created_at.desc())
            if limit:
                query = query.limit(limit)
            orders = query.all()
            for order in orders:
                session.expunge(order)
            return orders
    except SQLAlchemyError as e:
        print(f"Error getting orders: {e}")
        return []


# ===== POSITION OPERATIONS =====

def create_position(
    symbol: str,
    status: str,
    side: str,
    open_time: datetime,
    open_price: float,
    quantity: float,
    strategy_tag: Optional[str] = None,
    commission_open: float = 0,
    close_time: Optional[datetime] = None,
    close_price: Optional[float] = None,
    commission_close: float = 0,
    tags: Optional[Dict[str, Any]] = None,
    notes: Optional[str] = None
) -> Optional[Position]:
    """Create a new position record."""
    try:
        with get_db_session() as session:
            position = Position(
                symbol=symbol,
                strategy_tag=strategy_tag,
                status=status,
                side=side,
                open_time=open_time,
                open_price=open_price,
                quantity=quantity,
                commission_open=commission_open,
                close_time=close_time,
                close_price=close_price,
                commission_close=commission_close,
                tags=tags,
                notes=notes
            )
            session.add(position)
            session.flush()
            session.refresh(position)
            _ = position.id
            session.expunge(position)
            return position
    except SQLAlchemyError as e:
        print(f"Error creating position: {e}")
        return None


def get_position_by_id(position_id: int) -> Optional[Position]:
    """Get a position by its ID."""
    try:
        with get_db_session() as session:
            position = session.query(Position).filter(Position.id == position_id).first()
            if position:
                session.expunge(position)
            return position
    except SQLAlchemyError as e:
        print(f"Error getting position: {e}")
        return None


def get_positions_by_symbol(symbol: str) -> List[Position]:
    """Get all positions for a specific symbol."""
    try:
        with get_db_session() as session:
            positions = session.query(Position).filter(Position.symbol == symbol).all()
            for position in positions:
                session.expunge(position)
            return positions
    except SQLAlchemyError as e:
        print(f"Error getting positions: {e}")
        return []


def get_positions_by_status(status: str) -> List[Position]:
    """Get all positions with a specific status."""
    try:
        with get_db_session() as session:
            positions = session.query(Position).filter(Position.status == status).all()
            for position in positions:
                session.expunge(position)
            return positions
    except SQLAlchemyError as e:
        print(f"Error getting positions: {e}")
        return []


def update_position(position_id: int, **updates: Any) -> bool:
    """Update a position record by ID."""
    allowed_fields = {
        "symbol",
        "strategy_tag",
        "status",
        "side",
        "open_time",
        "open_price",
        "quantity",
        "commission_open",
        "close_time",
        "close_price",
        "commission_close",
        "tags",
        "notes"
    }
    update_data = {key: value for key, value in updates.items() if key in allowed_fields}
    if not update_data:
        return False
    try:
        with get_db_session() as session:
            session.query(Position).filter(Position.id == position_id).update(update_data)
            return True
    except SQLAlchemyError as e:
        print(f"Error updating position: {e}")
        return False


def delete_position(position_id: int) -> bool:
    """Delete a position by ID."""
    try:
        with get_db_session() as session:
            deleted = session.query(Position).filter(Position.id == position_id).delete()
            return bool(deleted)
    except SQLAlchemyError as e:
        print(f"Error deleting position: {e}")
        return False


def get_open_positions() -> List[Position]:
    """Get all open positions."""
    return get_positions_by_status("OPEN")
