"""Command-line entry point: `agentic-showcase run ...`."""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from .agent import Agent, Decision
from .brain import RuleBasedBrain
from .market import SimulatedMarket
from .portfolio import Portfolio


def _print_decision(d: Decision) -> None:
    print(
        f"tick {d.tick:4d}  price {d.price:8.2f}  "
        f"signal {d.signal.action:4s}  equity {d.equity:10,.2f}  "
        f"{'*' if d.executed else ' '} {d.signal.reason}"
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentic-showcase",
        description="Run an agentic paper-trading bot over a simulated market.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="run a backtest over the simulated market")
    run.add_argument("--symbol", default="REA", help="ticker label (cosmetic)")
    run.add_argument("--ticks", type=int, default=200, help="number of candles")
    run.add_argument("--seed", type=int, default=0, help="RNG seed (reproducible)")
    run.add_argument("--cash", type=float, default=10_000.0, help="starting cash")
    run.add_argument("--fast", type=int, default=10, help="fast SMA window")
    run.add_argument("--slow", type=int, default=30, help="slow SMA window")
    run.add_argument(
        "--risk",
        type=float,
        default=0.5,
        help="max fraction of cash to deploy per BUY (before confidence scaling)",
    )
    run.add_argument("--quiet", action="store_true", help="only print the summary")
    return parser


def _cmd_run(args: argparse.Namespace) -> int:
    market = SimulatedMarket(symbol=args.symbol, seed=args.seed)
    brain = RuleBasedBrain(fast=args.fast, slow=args.slow)
    agent = Agent(
        brain=brain,
        portfolio=Portfolio(cash=args.cash),
        max_risk_fraction=args.risk,
        on_decision=None if args.quiet else _print_decision,
    )

    result = agent.run(market.stream(args.ticks))

    print("\n=== summary ===")
    print(
        f"final equity {result.final_equity:12,.2f}   "
        f"return {result.total_return:+.2%}   "
        f"trades {result.trades}   "
        f"max drawdown {result.max_drawdown:.2%}"
    )
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.command == "run":
        return _cmd_run(args)
    parser.print_help()
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
