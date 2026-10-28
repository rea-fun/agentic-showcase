"""The agent loop: observe -> think -> act."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from . import tools
from .brain import Brain, Observation, Signal
from .market import Candle
from .portfolio import Portfolio


@dataclass
class Decision:
    """A full record of one agent step — useful for logging and tests."""

    tick: int
    price: float
    signal: Signal
    executed: bool
    equity: float


@dataclass
class Agent:
    """Drives a `Brain` against a market and a `Portfolio`.

    The agent owns risk policy (how much of cash to deploy per BUY, scaled by
    the brain's confidence). The brain owns the directional call. Keeping those
    separate is what lets you swap brains freely.
    """

    brain: Brain
    portfolio: Portfolio = field(default_factory=Portfolio)
    max_risk_fraction: float = 0.5
    on_decision: Optional[Callable[[Decision], None]] = None

    _prices: List[float] = field(default_factory=list, init=False)
    _equity_curve: List[float] = field(default_factory=list, init=False)
    _initial_equity: Optional[float] = field(default=None, init=False)
    history: List[Decision] = field(default_factory=list, init=False)

    def step(self, candle: Candle) -> Decision:
        """Process a single candle and return the resulting decision."""
        if self._initial_equity is None:
            # Baseline equity before any trade, marked at the first price.
            self._initial_equity = self.portfolio.equity(candle.price)
        self._prices.append(candle.price)
        obs = Observation(
            tick=candle.tick,
            price=candle.price,
            prices=list(self._prices),
            cash=self.portfolio.cash,
            shares=self.portfolio.shares,
        )

        signal = self.brain.decide(obs)
        executed = self._act(candle, signal)

        equity = self.portfolio.equity(candle.price)
        self._equity_curve.append(equity)

        decision = Decision(
            tick=candle.tick,
            price=candle.price,
            signal=signal,
            executed=executed,
            equity=equity,
        )
        self.history.append(decision)
        if self.on_decision is not None:
            self.on_decision(decision)
        return decision

    def _act(self, candle: Candle, signal: Signal) -> bool:
        if signal.action == "BUY":
            risk = self.max_risk_fraction * signal.confidence
            shares = tools.position_size(self.portfolio.cash, candle.price, risk)
            return self.portfolio.buy(candle.tick, shares, candle.price)
        if signal.action == "SELL":
            return self.portfolio.sell(candle.tick, self.portfolio.shares, candle.price)
        return False

    def run(self, candles) -> "RunResult":
        """Consume an iterable of candles and return summary statistics."""
        for candle in candles:
            self.step(candle)
        return self.summary()

    def summary(self) -> "RunResult":
        if not self._equity_curve:
            return RunResult(0.0, 0.0, 0, 0.0)
        baseline = self._initial_equity or self.portfolio.cash
        final = self._equity_curve[-1]
        ret = (final - baseline) / baseline if baseline else 0.0
        return RunResult(
            final_equity=final,
            total_return=ret,
            trades=self.portfolio.trade_count,
            max_drawdown=tools.max_drawdown(self._equity_curve),
        )


@dataclass
class RunResult:
    final_equity: float
    total_return: float
    trades: int
    max_drawdown: float
