#pragma once

#include <string>

enum class EventType {MARKET, SIGNAL, ORDER, FILL};
enum class Direction {SELL, BUY};

struct Bar {
    std::string ticker;
    long long timestamp;
    double open, high, low, close, volume;
};

struct Fill {
    std::string ticker;
    int quantity;
    double fill_price;
    double commission;
};

struct Order {
    std::string ticker;
    double quantity;
    double limit_price;
};

struct Signal {
    std::string strategy_id;
    std::string ticker;
    double value;
};