#pragma once

#include "unordered_map"

#include "Event.h"
#include "Context.h"

class DataHandler {
    public:
        virtual bool has_next() = 0;

        virtual std::unique_ptr<MarketEvent> next() = 0;

        void set_context(Context* context_);

    protected:
        Context* context = nullptr;
};

class CustomUniverseDataHandler : public DataHandler {
    public:
        bool has_next();
        std::unique_ptr<MarketEvent> next();
};