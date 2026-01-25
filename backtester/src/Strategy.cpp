#include "Strategy.h"

Strategy::~Strategy() = default;

void Strategy::on_start() {}

void Strategy::on_update(const MarketEvent&) {}

void Strategy::set_context(Context* context_) {
    context = context_;
}

void Strategy::send_signal(std::unique_ptr<Signal> signal) {
    if (context == nullptr || context->sink == nullptr) {
        return;
    }

    auto se = std::make_unique<SignalEvent>();
    se->signal = std::move(signal);
    context->sink->publish(std::move(se));
}