#pragma once

#include "unordered_map"

#include "Event.h"

class DataHandler {
    public:
        virtual bool has_next() = 0;

        virtual MarketEvent next() = 0;
};

class CustomUniverseDataHandler : public DataHandler {
    public:
        bool has_next();
        MarketEvent next();
};