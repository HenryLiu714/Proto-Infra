#include "Engine.h"

Engine::Engine(const EngineConfig& config_, std::shared_ptr<DataHandler> data_handler_) {
    config = config_;
    data_handler = data_handler_;

    execution_handler = std::make_shared<ExecutionHandler>();
    event_queue = {};
}

void Engine::set_config(const EngineConfig& config_) {
    config = config_;
}

void Engine::set_data_handler(std::shared_ptr<DataHandler> data_handler_) {
    data_handler = data_handler_;
}

void Engine::set_strategy(std::shared_ptr<Strategy> strategy_) {
    strategy = strategy_;
}

void Engine::set_portfolio(std::shared_ptr<Portfolio> portfolio_) {
    portfolio = portfolio_;
}

void Engine::run_backtest() {
    // 1. Initialize strategy
    strategy->on_start();

    // 2. Start backtest
    while (data_handler->has_next()) {

    }
}