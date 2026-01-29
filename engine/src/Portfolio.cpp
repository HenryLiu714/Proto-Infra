#include <memory>

#include "Context.h"
#include "Portfolio.h"

Portfolio::~Portfolio() = default;

void Portfolio::on_signal(const Signal&) {}

void Portfolio::on_fill(const Fill&) {}

void Portfolio::send_order(std::unique_ptr<Order> order) {
    if (context == nullptr || context->sink == nullptr) {
        return;
    }

    // Wrap in OrderEvent and publish to EventSink
    auto order_event = std::make_unique<OrderEvent>();
    order_event->order = std::move(order);
    context->sink->publish(std::move(order_event));
}

void Portfolio::set_context(Context* context_) {
    context = context_;
}