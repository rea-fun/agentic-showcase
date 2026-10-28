"""Tools the agent's brain can call.

Each tool is a small, pure function over a window of recent prices (or the
portfolio state). They're deliberately dependency-free — no numpy — so the
repo stays trivial to run. A brain composes them into a decision.
"""

from __future__ import annotations

from typing import List, Optional


def sma(prices: List[float], window: int) -> Optional[float]:
    """Simple moving average of the last `window` prices, or None if too short."""
    if window <= 0 or len(prices) < window:
        return None
    return sum(prices[-window:]) / window


def rsi(prices: List[float], window: int = 14) -> Optional[float]:
    """Relative Strength Index (Wilder's smoothing), range 0..100."""
    if len(prices) < window + 1:
        return None

    gains = 0.0
    losses = 0.0
    for i in range(-window, 0):
        change = prices[i] - prices[i - 1]
        if change >= 0:
            gains += change
        else:
            losses -= change

    avg_gain = gains / window
    avg_loss = losses / window
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def volatility(prices: List[float], window: int = 20) -> Optional[float]:
    """Sample standard deviation of returns over `window`, as a fraction."""
    if len(prices) < window + 1:
        return None

    rets = []
    for i in range(-window, 0):
        prev = prices[i - 1]
        if prev == 0:
            continue
        rets.append((prices[i] - prev) / prev)
    if len(rets) < 2:
        return None

    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    return var**0.5


def position_size(cash: float, price: float, risk_fraction: float) -> int:
    """How many whole shares to buy spending at most `risk_fraction` of cash."""
    if price <= 0 or risk_fraction <= 0 or cash <= 0:
        return 0
    budget = cash * min(risk_fraction, 1.0)
    return int(budget // price)


def max_drawdown(equity_curve: List[float]) -> float:
    """Largest peak-to-trough drop in the equity curve, as a negative fraction."""
    if not equity_curve:
        return 0.0
    peak = equity_curve[0]
    worst = 0.0
    for value in equity_curve:
        peak = max(peak, value)
        if peak > 0:
            worst = min(worst, (value - peak) / peak)
    return worst
