"""agentic-showcase: a tiny agentic paper-trading bot.

Public surface kept small on purpose — import the pieces you need:

    from agentic_showcase import Agent, RuleBasedBrain, SimulatedMarket, Portfolio
"""

from .agent import Agent, Decision
from .brain import Brain, RuleBasedBrain
from .market import Candle, SimulatedMarket
from .portfolio import Portfolio

__version__ = "0.1.0"

__all__ = [
    "Agent",
    "Decision",
    "Brain",
    "RuleBasedBrain",
    "Candle",
    "SimulatedMarket",
    "Portfolio",
    "__version__",
]
