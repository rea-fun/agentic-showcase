"""Market data sources.

`SimulatedMarket` is a deterministic geometric-random-walk generator so that
runs are reproducible from a seed. `LiveMarket` is a stub showing where a real
exchange / data-vendor adapter would plug in.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterator, List


@dataclass(frozen=True)
class Candle:
    """A single OHLCV bar."""

    tick: int
    open: float
    high: float
    low: float
    close: float
    volume: float

    @property
    def price(self) -> float:
        """Convenience alias used by the agent — the close is the mark price."""
        return self.close


class SimulatedMarket:
    """Deterministic price series via a seeded geometric random walk.

    The walk has a mild upward drift plus volatility clustering so that the
    indicator tools actually have something to chew on. Same seed -> same path.
    """

    def __init__(
        self,
        *,
        symbol: str = "REA",
        start_price: float = 100.0,
        drift: float = 0.0004,
        volatility: float = 0.012,
        seed: int = 0,
    ) -> None:
        self.symbol = symbol
        self.start_price = start_price
        self.drift = drift
        self.volatility = volatility
        self._rng = random.Random(seed)
        self._price = start_price
        self._vol = volatility
        self._tick = 0

    def _step(self) -> Candle:
        # Volatility clustering: today's vol drifts toward the baseline.
        shock = self._rng.gauss(0.0, 1.0)
        self._vol = 0.9 * self._vol + 0.1 * self.volatility * (1.0 + abs(shock))
        ret = self.drift + self._vol * shock
        prev = self._price
        close = max(0.01, prev * math.exp(ret))

        high = max(prev, close) * (1.0 + abs(self._rng.gauss(0, self._vol / 2)))
        low = min(prev, close) * (1.0 - abs(self._rng.gauss(0, self._vol / 2)))
        volume = round(1000 * (1.0 + abs(shock)), 2)

        candle = Candle(
            tick=self._tick,
            open=round(prev, 4),
            high=round(high, 4),
            low=round(low, 4),
            close=round(close, 4),
            volume=volume,
        )
        self._price = close
        self._tick += 1
        return candle

    def stream(self, ticks: int) -> Iterator[Candle]:
        """Yield `ticks` candles."""
        for _ in range(ticks):
            yield self._step()

    def history(self, ticks: int) -> List[Candle]:
        """Materialize `ticks` candles into a list."""
        return list(self.stream(ticks))


class LiveMarket:
    """Placeholder for a real data feed.

    Wire this up to a broker/data vendor (e.g. a websocket or REST poll) and
    yield `Candle` objects. Kept as a stub so the showcase has no network deps.
    """

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol

    def stream(self, ticks: int) -> Iterator[Candle]:  # pragma: no cover - stub
        raise NotImplementedError(
            "LiveMarket is a stub. Plug in a real data source here, or use "
            "SimulatedMarket for the showcase."
        )
