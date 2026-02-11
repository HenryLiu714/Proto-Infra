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