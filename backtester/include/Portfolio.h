#pragma once

#include <unordered_map>

#include "Event.h"

struct Position {
    std::string ticker;
    int quantity;
    double entry_price;
    double current_price;
    long long entry_timestamp;
};

class Portfolio {
    public:
        virtual ~Portfolio();
        virtual void on_signals(const std::vector<SignalEvent>);

    protected:
        double cash;
        std::unordered_map<std::string, double> active_positions;
};