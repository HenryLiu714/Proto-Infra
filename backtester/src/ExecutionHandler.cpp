
#include "ExecutionHandler.h"


double ExecutionHandler::calculate_commission(double quantity, double share_price) {
    double commission_cost = commission * std::abs(quantity);

    double total_cost = quantity * share_price;

    return std::min(0.01 * total_cost, commission_cost);
}

std::vector<std::shared_ptr<FillEvent>> ExecutionHandler::on_market_update(std::shared_ptr<MarketEvent> update) {
    // Update current prices and execute orders
    std::unordered_map<std::string, Bar>* bars = &update->bars;

    for (const std::shared_ptr<OrderEvent> order: pending_orders) {
        if (bars->find(order->ticker) != bars->end()) {
            // Check if
        }
    }
}

void ExecutionHandler::submit_order(std::shared_ptr<OrderEvent> order) {

}