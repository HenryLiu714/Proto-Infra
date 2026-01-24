#pragma once

#include <memory>

#include "Event.h"

class ExecutionHandler {
    public:
        ExecutionHandler(double slippage = 0.0005, double commission = 0.35);

        std::vector<std::shared_ptr<FillEvent>> on_market_update(std::shared_ptr<MarketEvent> update);
        void submit_order(std::shared_ptr<OrderEvent> order);

    private:
        double slippage;
        double commission; // Price per share

        std::vector<std::shared_ptr<OrderEvent>> pending_orders;

        double calculate_commission(double quantity, double share_price);
};