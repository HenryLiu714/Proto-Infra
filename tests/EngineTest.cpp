#include <deque>
#include <gtest/gtest.h>

#include "Context.h"
#include "DataHandler.h"
#include "Engine.h"
#include "Portfolio.h"
#include "Strategy.h"

struct TestSink : public EventSink {
    std::vector<std::unique_ptr<Event>> events;
    void publish(std::unique_ptr<Event> event) override { events.push_back(std::move(event)); }
};

struct RecordingDataHandler : public DataHandler {
    explicit RecordingDataHandler(std::deque<std::unique_ptr<MarketEvent>> events_) : events(std::move(events_)) {}

    bool has_next() override { return !events.empty(); }

    std::unique_ptr<MarketEvent> next() override {
        auto ev = std::move(events.front());
        events.pop_front();
        return ev;
    }

    bool has_context() const { return context != nullptr; }

    std::deque<std::unique_ptr<MarketEvent>> events;
};

struct RecordingPortfolio : public Portfolio {
    void on_signal(const Signal& signal) override {
        signal_count++;
        last_signal = signal.ticker;

        auto order = std::make_unique<Order>(Order{OrderType::MARKET, signal.ticker, Direction::BUY, 5, 0});
        send_order(std::move(order));
    }

    void on_fill(const Fill& fill) override {
        fill_count++;
        last_fill = fill;
    }

    int signal_count = 0;
    int fill_count = 0;
    std::string last_signal;
    Fill last_fill{};
};

struct SignalEmittingStrategy : public Strategy {
    explicit SignalEmittingStrategy(std::string ticker_ = "AAPL") : ticker(std::move(ticker_)) {}

    void on_start() override {
        started = true;
        emit_signal(ticker);
    }

    void on_update(const MarketEvent& event) override {
        if (emitted || event.bars.empty()) {
            return;
        }

        emit_signal(event.bars.begin()->first);
    }

    void emit_signal(const std::string& symbol) {
        auto sig = std::make_unique<Signal>();
        sig->strategy_id = "test";
        sig->ticker = symbol;
        sig->value = 1.0;
        send_signal(std::move(sig));
        emitted = true;
    }

    std::string ticker;
    bool started = false;
    bool emitted = false;
};

std::unique_ptr<MarketEvent> make_market_event(const std::string& ticker, double open) {
    auto me = std::make_unique<MarketEvent>();
    me->bars[ticker] = Bar{ticker, 0, open, open, open, open, 1000};
    return me;
}

TEST(DataHandlerTest, StoresContextWhenSet) {
    RecordingDataHandler handler({});
    TestSink sink;
    Context ctx{&sink};

    handler.set_context(&ctx);

    EXPECT_TRUE(handler.has_context());
}

TEST(PortfolioTest, SendOrderPublishesOrderEvent) {
    RecordingPortfolio portfolio;
    TestSink sink;
    Context ctx{&sink};
    portfolio.set_context(&ctx);

    auto order = std::make_unique<Order>(Order{OrderType::MARKET, "AAPL", Direction::BUY, 10, 0});
    portfolio.send_order(std::move(order));

    ASSERT_EQ(sink.events.size(), 1u);
    auto* oe = dynamic_cast<OrderEvent*>(sink.events.front().get());
    ASSERT_NE(oe, nullptr);
    ASSERT_NE(oe->order, nullptr);
    EXPECT_EQ(oe->order->ticker, "AAPL");
    EXPECT_EQ(oe->order->quantity, 10);
}

TEST(PortfolioTest, SendOrderWithoutContextDoesNothing) {
    RecordingPortfolio portfolio;

    auto order = std::make_unique<Order>(Order{OrderType::MARKET, "AAPL", Direction::BUY, 10, 0});
    portfolio.send_order(std::move(order));

    // No context wired, so no events should be emitted
    // (would crash if context sink were dereferenced)
    SUCCEED();
}

TEST(StrategyTest, SendSignalPublishesToSink) {
    SignalEmittingStrategy strategy;
    TestSink sink;
    Context ctx{&sink};
    strategy.set_context(&ctx);

    auto me = make_market_event("AAPL", 100.0);
    strategy.on_start();
    strategy.on_update(*me);

    ASSERT_TRUE(strategy.started);
    ASSERT_EQ(sink.events.size(), 1u);
    auto* se = dynamic_cast<SignalEvent*>(sink.events.front().get());
    ASSERT_NE(se, nullptr);
    ASSERT_NE(se->signal, nullptr);
    EXPECT_EQ(se->signal->ticker, "AAPL");
    EXPECT_DOUBLE_EQ(se->signal->value, 1.0);
}

struct StartOnlyStrategy : public Strategy {
    void on_start() override {
        auto sig = std::make_unique<Signal>();
        sig->ticker = "AAPL";
        send_signal(std::move(sig));
    }
};

TEST(StrategyTest, SendSignalIgnoredWithoutSink) {
    StartOnlyStrategy strategy;
    Context ctx{nullptr};
    strategy.set_context(&ctx);

    strategy.on_start();

    // No sink so nothing is published and no crash occurs
    SUCCEED();
}

struct ContextRecordingDataHandler : public DataHandler {
    bool has_next() override { return false; }
    std::unique_ptr<MarketEvent> next() override { return nullptr; }
    bool context_set() const { return context != nullptr; }
};

struct ContextRecordingStrategy : public Strategy {
    void on_update(const MarketEvent&) override {}
    bool context_set() const { return context != nullptr; }
};

struct ContextRecordingPortfolio : public Portfolio {
    void on_signal(const Signal&) override {}
    bool context_set() const { return context != nullptr; }
};

TEST(EngineTest, SetsContextOnComponents) {
    auto dh = std::make_shared<ContextRecordingDataHandler>();
    EngineConfig cfg;
    Engine engine(cfg, dh);

    auto strat = std::make_shared<ContextRecordingStrategy>();
    auto port = std::make_shared<ContextRecordingPortfolio>();
    engine.set_strategy(strat);
    engine.set_portfolio(port);

    EXPECT_TRUE(dh->context_set());
    EXPECT_TRUE(strat->context_set());
    EXPECT_TRUE(port->context_set());
}

struct NoOpDataHandler : public DataHandler {
    explicit NoOpDataHandler(std::unique_ptr<MarketEvent> ev) : event(std::move(ev)) {}
    bool has_next() override { return event != nullptr; }
    std::unique_ptr<MarketEvent> next() override {
        return std::move(event);
    }
    std::unique_ptr<MarketEvent> event;
};

struct FillRecordingPortfolio : public Portfolio {
    void on_fill(const Fill& fill) override {
        fills.push_back(fill);
    }
    std::vector<Fill> fills;
};

TEST(EngineTest, ProcessesPublishedEventsThroughQueue) {
    // Preload a fill event to the engine queue, then run a single-iteration backtest
    auto dh = std::make_shared<NoOpDataHandler>(make_market_event("AAPL", 100.0));
    EngineConfig cfg;
    Engine engine(cfg, dh);

    auto port = std::make_shared<FillRecordingPortfolio>();
    engine.set_portfolio(port);
    auto strat = std::make_shared<SignalEmittingStrategy>("AAPL");
    engine.set_strategy(strat);

    auto fe = std::make_unique<FillEvent>();
    fe->fill = std::make_unique<Fill>(Fill{"AAPL", 1, 99.0, 0.1});
    engine.publish(std::move(fe));

    engine.run_backtest();

    ASSERT_FALSE(port->fills.empty());
    EXPECT_EQ(port->fills.front().fill_price, 99.0);
}

TEST(EngineTest, RunsBacktestThroughSignalOrderFill) {
    std::deque<std::unique_ptr<MarketEvent>> events;
    events.push_back(make_market_event("AAPL", 100.0));
    events.push_back(make_market_event("AAPL", 101.0));
    auto dh = std::make_shared<RecordingDataHandler>(std::move(events));

    auto strategy = std::make_shared<SignalEmittingStrategy>("AAPL");
    auto portfolio = std::make_shared<RecordingPortfolio>();

    EngineConfig cfg;
    Engine engine(cfg, dh);
    engine.set_strategy(strategy);
    engine.set_portfolio(portfolio);

    engine.run_backtest();

    EXPECT_TRUE(strategy->started);
    EXPECT_EQ(portfolio->signal_count, 1);
    EXPECT_EQ(portfolio->fill_count, 1);
    EXPECT_EQ(portfolio->last_fill.ticker, "AAPL");
    EXPECT_EQ(portfolio->last_fill.fill_price, 101.0);
}
