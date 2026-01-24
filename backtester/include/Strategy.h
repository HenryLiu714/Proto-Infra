#pragma once

#include "Event.h"

class Strategy {
    public:
        virtual ~Strategy();

        virtual void on_start();

        // Called on universe update
        virtual void on_update(const MarketEvent& event);

        // Send signal
        void send_signals(const std::vector<Signal>& signals);
};