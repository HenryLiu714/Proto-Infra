"""Example usage of the database package."""

from db import (
    test_connection,
    create_order,
    create_fill,
    get_order_by_id,
    get_all_orders
)


def main():
    """Demonstrate database operations."""

    # Test connection
    print("Testing database connection...")
    if test_connection():
        print("✓ Connection successful!\n")
    else:
        print("✗ Connection failed!\n")
        return

    # Example: Create an order
    print("Creating an order...")
    order = create_order(
        order_id="ORD123456",
        symbol="AAPL",
        quantity_ordered=100,
        status="pending"
    )
    if order:
        print(f"✓ Order created: {order.to_dict()}\n")

    # Example: Create a fill for the order
    print("Creating a fill...")
    fill = create_fill(
        order_id="ORD123456",
        quantity=50,
        price=150.25
    )
    if fill:
        print(f"✓ Fill created: {fill.to_dict()}\n")

    # Example: Get order by ID
    print("Retrieving order...")
    retrieved_order = get_order_by_id("ORD123456")
    if retrieved_order:
        print(f"✓ Order retrieved: {retrieved_order.to_dict()}\n")

    # Example: Get all orders
    print("Getting all orders...")
    all_orders = get_all_orders(limit=10)
    print(f"✓ Found {len(all_orders)} orders\n")


if __name__ == "__main__":
    main()
