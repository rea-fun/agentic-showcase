# agentic-showcase

A small, self-contained **agentic paper-trading bot** written in Python.

An autonomous agent runs a simple *observe → think → act* loop. On each tick it
calls a set of pluggable **tools** (market data, technical indicators, position
sizing, risk checks), feeds the observations to a **brain**, and executes the
resulting decision against a paper-trading portfolio. No real money, no API keys
required — it ships with a deterministic market simulator so you can `git clone`
and run it immediately.

```
   ┌────────────┐     observe     ┌─────────────┐
   │   Market   │ ───────────────▶│    Agent    │
   │ (sim/live) │                 │   loop      │
   └────────────┘                 └──────┬──────┘
         ▲                                │ think (brain)
         │ act (orders)                   ▼
   ┌─────┴──────┐                 ┌─────────────┐
   │ Portfolio  │◀────────────────│  Decision   │
   │  (paper)   │                 │ BUY/SELL/HOLD│
   └────────────┘                 └─────────────┘
```

## Why "agentic"?

The agent doesn't hard-code a single strategy. It exposes a toolbox and a
`Brain` interface. The default `RuleBasedBrain` reasons over indicator tools
(SMA crossover, RSI, volatility) and a risk budget to pick an action. You can
drop in an LLM-backed brain (`llm_brain.py` sketches the adapter) without
touching the agent loop.

## Quickstart

```bash
pip install -e .
# run a backtest over the built-in simulated market
agentic-showcase run --symbol REA --ticks 200 --seed 7

# or from Python
python examples/backtest.py
```

Example output:

```
tick  042  price   103.44  signal BUY   cash   4,812.00  shares  48  equity  9,775.12
tick  043  price   104.01  signal HOLD  cash   4,812.00  shares  48  equity  9,802.48
...
=== summary ===
final equity   10,431.57   return  +4.32%   trades 11   max drawdown -3.11%
```

## Layout

| Path | What it does |
| --- | --- |
| `agentic_showcase/agent.py` | The observe→think→act loop |
| `agentic_showcase/brain.py` | `Brain` interface + `RuleBasedBrain` |
| `agentic_showcase/tools.py` | Indicator/risk tools the brain can call |
| `agentic_showcase/market.py` | Deterministic market simulator + live adapter hook |
| `agentic_showcase/portfolio.py` | Paper-trading accounting |
| `agentic_showcase/cli.py` | `agentic-showcase` command-line entry point |
| `agentic_showcase/llm_brain.py` | Optional LLM-backed brain adapter |
| `examples/backtest.py` | End-to-end runnable demo |
| `tests/` | pytest suite |

## Disclaimer

This is an educational showcase. It is **not** financial advice and is not wired
to any real exchange. The "live" market adapter is a stub.

## License

MIT — see [LICENSE](LICENSE).
