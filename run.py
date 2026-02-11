#!/usr/bin/env python3
"""Entry point for the trading infrastructure application.

Run this script from the project root directory.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now we can import from src
from src.Engine import Engine
from src.Strategy import Strategy
from src.Portfolio import Portfolio
from src.Alert import send_alert


def main():
    """Run the trading engine."""
    send_alert("Starting Trading Engine...")

    engine = Engine()

    strategy = Strategy("Testing Strategy")
    portfolio = Portfolio()

    engine.strategy = strategy
    engine.portfolio = portfolio

    engine.run()


if __name__ == "__main__":
    main()
