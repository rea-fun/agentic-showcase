"""Paper-trading portfolio accounting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal

Side = Literal["BUY", "SELL"]


@dataclass
class Fill:
    """A recorded execution."""

    tick: int
    side: Side
    shares: int
    price: float

    @property
    def notional(self) -> float:
        return self.shares * self.price


@dataclass
class Portfolio:
    """Tracks cash, share count, and a trade log.

    A flat fee + proportional slippage are applied to every fill so the
    backtest doesn't look unrealistically perfect.
    """

    cash: float = 10_000.0
    shares: int = 0
    fee: float = 1.0
    slippage: float = 0.0005
    fills: List[Fill] = field(default_factory=list)

    def equity(self, price: float) -> float:
        """Mark-to-market total value."""
        return self.cash + self.shares * price

    def can_buy(self, shares: int, price: float) -> bool:
        if shares <= 0:
            return False
        cost = shares * price * (1 + self.slippage) + self.fee
        return cost <= self.cash

    def buy(self, tick: int, shares: int, price: float) -> bool:
        if not self.can_buy(shares, price):
            return False
        exec_price = price * (1 + self.slippage)
        self.cash -= shares * exec_price + self.fee
        self.shares += shares
        self.fills.append(Fill(tick, "BUY", shares, round(exec_price, 4)))
        return True

    def sell(self, tick: int, shares: int, price: float) -> bool:
        shares = min(shares, self.shares)
        if shares <= 0:
            return False
        exec_price = price * (1 - self.slippage)
        self.cash += shares * exec_price - self.fee
        self.shares -= shares
        self.fills.append(Fill(tick, "SELL", shares, round(exec_price, 4)))
        return True

    @property
    def trade_count(self) -> int:
        return len(self.fills)
