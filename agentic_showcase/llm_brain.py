"""Optional LLM-backed brain.

This is a *sketch* of how you'd swap the rule-based policy for a language model
without changing the agent loop. It intentionally has no hard dependency on any
SDK: it describes the tool outputs in a prompt, asks the model for a JSON
decision, and falls back to the rule-based brain if anything is unavailable.

To make it live, implement `_complete()` against your provider of choice
(Anthropic, OpenAI, a local model, ...).
"""

from __future__ import annotations

import json
from typing import Optional

from . import tools
from .brain import Brain, Observation, RuleBasedBrain, Signal

SYSTEM_PROMPT = """You are a disciplined trading agent. Given technical
indicators for a single asset, respond with ONLY a JSON object:
{"action": "BUY"|"SELL"|"HOLD", "confidence": 0.0-1.0, "reason": "..."}.
Be conservative: prefer HOLD when signals conflict."""


class LLMBrain(Brain):
    """Delegates the decision to a language model, with a safe fallback."""

    def __init__(self, *, model: str = "claude-sonnet-4-6", fallback: Optional[Brain] = None) -> None:
        self.model = model
        self.fallback = fallback or RuleBasedBrain()

    def _features(self, obs: Observation) -> dict:
        prices = obs.prices
        return {
            "price": obs.price,
            "sma_fast": tools.sma(prices, 10),
            "sma_slow": tools.sma(prices, 30),
            "rsi": tools.rsi(prices, 14),
            "volatility": tools.volatility(prices, 20),
            "cash": obs.cash,
            "shares": obs.shares,
        }

    def _complete(self, prompt: str) -> Optional[str]:  # pragma: no cover - stub
        """Return the model's raw text, or None if no provider is configured.

        Replace the body with a real API call, e.g.:

            from anthropic import Anthropic
            client = Anthropic()
            msg = client.messages.create(
                model=self.model,
                max_tokens=256,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        """
        return None

    def decide(self, obs: Observation) -> Signal:
        features = self._features(obs)
        prompt = f"Indicators:\n{json.dumps(features, indent=2)}\n\nDecision JSON:"
        raw = self._complete(prompt)
        if not raw:
            return self.fallback.decide(obs)
        try:
            data = json.loads(raw)
            action = str(data["action"]).upper()
            if action not in {"BUY", "SELL", "HOLD"}:
                raise ValueError(f"bad action {action!r}")
            return Signal(
                action=action,
                confidence=float(data.get("confidence", 0.5)),
                reason=str(data.get("reason", "llm decision")),
            )
        except (json.JSONDecodeError, KeyError, ValueError, TypeError):
            # Malformed model output -> fail safe to the deterministic brain.
            return self.fallback.decide(obs)
