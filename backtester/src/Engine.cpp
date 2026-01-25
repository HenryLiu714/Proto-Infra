#include "Engine.h"

Engine::Engine(const EngineConfig& config_, std::shared_ptr<DataHandler> data_handler_) {
    config = config_;
    data_handler = data_handler_;

    execution_handler = std::make_unique<ExecutionHandler>();
    context = Context{this};

    execution_handler->set_context(&context);

    if (data_handler) {
        data_handler->set_context(&context);
    }
}

Engine::~Engine() = default;

void Engine::publish(std::unique_ptr<Event> event) {
    // Push incoming events (Order/Fill/Signal) onto the engine queue for processing
    event_queue.push_back(std::move(event));
}

void Engine::set_config(const EngineConfig& config_) {
    config = config_;
}

void Engine::set_data_handler(std::shared_ptr<DataHandler> data_handler_) {
    data_handler = data_handler_;

    if (data_handler) {
        data_handler->set_context(&context);
    }
}

void Engine::set_strategy(std::shared_ptr<Strategy> strategy_) {
    strategy = strategy_;

    if (strategy) {
        strategy->set_context(&context);
    }
}

void Engine::set_portfolio(std::shared_ptr<Portfolio> portfolio_) {
    portfolio = portfolio_;

    if (portfolio) {
        portfolio->set_context(&context);
    }
}

void Engine::run_backtest() {
    // 1. Initialize strategy
    strategy->on_start();

    // 2. Start backtest
    while (data_handler->has_next()) {
        // Queue should be empty at this point
        event_queue.push_back(data_handler->next());

        // 4. Now iterate through event queue
        while (!event_queue.empty()) {
            std::unique_ptr<Event> event = std::move(event_queue.front());
            event_queue.pop_front();

            switch (event->type) {
                case EventType::MARKET: {
                    MarketEvent& market_event = dynamic_cast<MarketEvent&>(*event);

                    execution_handler->on_market_update(market_event);
                    strategy->on_update(market_event);
                    break;
                }

                case EventType::SIGNAL: {
                    SignalEvent& signal_event = dynamic_cast<SignalEvent&>(*event);
                    portfolio->on_signal(*signal_event.signal);
                    break;
                }

                case EventType::ORDER: {
                    OrderEvent& order_event = dynamic_cast<OrderEvent&>(*event);
                    execution_handler->submit_order(std::move(order_event.order));
                    break;
                }

                case EventType::FILL: {
                    FillEvent& fill_event = dynamic_cast<FillEvent&>(*event);
                    portfolio->on_fill(*fill_event.fill);
                    break;
                }
            }
        }
    }
}