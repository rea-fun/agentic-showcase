from agentic_showcase import Agent, Portfolio, RuleBasedBrain, SimulatedMarket
from agentic_showcase.brain import Brain, Observation, Signal


class AlwaysBuyBrain(Brain):
    def decide(self, obs: Observation) -> Signal:
        return Signal("BUY", 1.0, "always buy")


class AlwaysSellBrain(Brain):
    def decide(self, obs: Observation) -> Signal:
        return Signal("SELL", 1.0, "always sell")


def test_simulated_market_is_deterministic():
    a = SimulatedMarket(seed=42).history(50)
    b = SimulatedMarket(seed=42).history(50)
    assert [c.close for c in a] == [c.close for c in b]


def test_different_seeds_diverge():
    a = SimulatedMarket(seed=1).history(50)
    b = SimulatedMarket(seed=2).history(50)
    assert [c.close for c in a] != [c.close for c in b]


def test_agent_run_produces_summary():
    agent = Agent(brain=RuleBasedBrain(), portfolio=Portfolio(cash=10_000.0))
    result = agent.run(SimulatedMarket(seed=7).stream(200))
    assert len(agent.history) == 200
    assert result.trades >= 0
    assert result.max_drawdown <= 0.0
    assert result.final_equity > 0


def test_always_buy_deploys_cash():
    agent = Agent(
        brain=AlwaysBuyBrain(),
        portfolio=Portfolio(cash=10_000.0),
        max_risk_fraction=0.5,
    )
    agent.run(SimulatedMarket(seed=3).stream(20))
    assert agent.portfolio.shares > 0


def test_always_sell_never_goes_short():
    agent = Agent(brain=AlwaysSellBrain(), portfolio=Portfolio(cash=10_000.0))
    agent.run(SimulatedMarket(seed=3).stream(20))
    assert agent.portfolio.shares == 0


def test_warmup_holds():
    # With only a handful of ticks the brain can't compute the slow SMA.
    agent = Agent(brain=RuleBasedBrain(fast=10, slow=30))
    agent.run(SimulatedMarket(seed=5).stream(5))
    assert all(d.signal.action == "HOLD" for d in agent.history)
