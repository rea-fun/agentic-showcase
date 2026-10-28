"""The decision-making layer.

`Brain` is the interface the agent calls on every tick. `RuleBasedBrain` is a
transparent, deterministic implementation that composes the indicator tools
into a trade signal. Swap in another `Brain` (e.g. `llm_brain.LLMBrain`) to
change the policy without touching the agent loop.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from . import tools


@dataclass
class Observation:
    """Everything the brain sees on a single tick."""

    tick: int
    price: float
    prices: List[float]  # full price history up to and including `price`
    cash: float
    shares: int


@dataclass
class Signal:
    """A brain's recommendation."""

    action: str  # "BUY" | "SELL" | "HOLD"
    confidence: float  # 0..1
    reason: str


class Brain(Protocol):
    """Any object that can turn an observation into a signal."""

    def decide(self, obs: Observation) -> Signal: ...


class RuleBasedBrain:
    """SMA-crossover + RSI filter, scaled down in high-volatility regimes.

    Logic:
      * Fast SMA crossing above slow SMA and RSI not overbought  -> BUY
      * Fast SMA crossing below slow SMA or RSI overbought        -> SELL
      * otherwise                                                 -> HOLD
    Confidence shrinks as volatility rises, which the agent uses to size down.
    """

    def __init__(
        self,
        *,
        fast: int = 10,
        slow: int = 30,
        rsi_window: int = 14,
        rsi_overbought: float = 70.0,
        rsi_oversold: float = 30.0,
    ) -> None:
        if fast >= slow:
            raise ValueError("fast window must be shorter than slow window")
        self.fast = fast
        self.slow = slow
        self.rsi_window = rsi_window
        self.rsi_overbought = rsi_overbought
        self.rsi_oversold = rsi_oversold

    def decide(self, obs: Observation) -> Signal:
        prices = obs.prices
        fast_now = tools.sma(prices, self.fast)
        slow_now = tools.sma(prices, self.slow)
        fast_prev = tools.sma(prices[:-1], self.fast)
        slow_prev = tools.sma(prices[:-1], self.slow)

        if None in (fast_now, slow_now, fast_prev, slow_prev):
            return Signal("HOLD", 0.0, "warming up: not enough history")

        rsi_now = tools.rsi(prices, self.rsi_window) or 50.0
        vol = tools.volatility(prices) or 0.0
        # Confidence decays with volatility; clamp to [0.1, 1.0].
        confidence = max(0.1, min(1.0, 1.0 - vol * 25))

        crossed_up = fast_prev <= slow_prev and fast_now > slow_now
        crossed_down = fast_prev >= slow_prev and fast_now < slow_now

        if crossed_up and rsi_now < self.rsi_overbought:
            return Signal(
                "BUY",
                confidence,
                f"golden cross (fast {fast_now:.2f} > slow {slow_now:.2f}), "
                f"RSI {rsi_now:.0f}",
            )
        if crossed_down or rsi_now >= self.rsi_overbought:
            why = "death cross" if crossed_down else f"RSI overbought {rsi_now:.0f}"
            return Signal("SELL", confidence, why)
        if rsi_now <= self.rsi_oversold and fast_now > slow_now:
            return Signal("BUY", confidence * 0.8, f"oversold bounce, RSI {rsi_now:.0f}")

        return Signal("HOLD", confidence, f"no cross; RSI {rsi_now:.0f}")
