#pragma once

#include <string>
#include <vector>
#include <unordered_map>
#include <memory>

#include "Types.h"

struct Event {
    virtual ~Event() = default;

    EventType type;
    long long timestamp;
};

// Notification of new data
struct MarketEvent : public Event {
    MarketEvent() {type = EventType::MARKET;}
    std::unordered_map<std::string, Bar> bars;
};

struct SignalEvent : public Event {
    SignalEvent() {type = EventType::SIGNAL;}
    std::unique_ptr<Signal> signal;

};

struct OrderEvent : public Event {
    OrderEvent() {type = EventType::ORDER;}
    std::unique_ptr<Order> order;
};

struct FillEvent : public Event {
    FillEvent() {type = EventType::FILL;}
    std::unique_ptr<Fill> fill;
};
