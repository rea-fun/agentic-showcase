"""End-to-end demo: run the agent over a simulated market and print a report.

    python examples/backtest.py
"""

from __future__ import annotations

from agentic_showcase import Agent, Portfolio, RuleBasedBrain, SimulatedMarket


def main() -> None:
    market = SimulatedMarket(symbol="REA", seed=7)
    agent = Agent(
        brain=RuleBasedBrain(fast=10, slow=30),
        portfolio=Portfolio(cash=10_000.0),
        max_risk_fraction=0.5,
    )

    result = agent.run(market.stream(200))

    # Show the last few decisions for flavour.
    for decision in agent.history[-5:]:
        print(
            f"tick {decision.tick:3d}  {decision.signal.action:4s}  "
            f"price {decision.price:7.2f}  equity {decision.equity:10,.2f}  "
            f"({decision.signal.reason})"
        )

    print("\n=== summary ===")
    print(f"final equity : {result.final_equity:,.2f}")
    print(f"total return : {result.total_return:+.2%}")
    print(f"trades       : {result.trades}")
    print(f"max drawdown : {result.max_drawdown:.2%}")


if __name__ == "__main__":
    main()
