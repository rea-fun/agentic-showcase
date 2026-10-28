from agentic_showcase import Portfolio


def test_buy_reduces_cash_and_adds_shares():
    p = Portfolio(cash=1000.0, fee=0.0, slippage=0.0)
    assert p.buy(tick=0, shares=5, price=100.0) is True
    assert p.shares == 5
    assert p.cash == 500.0
    assert p.trade_count == 1


def test_buy_rejected_when_insufficient_cash():
    p = Portfolio(cash=100.0, fee=0.0, slippage=0.0)
    assert p.buy(tick=0, shares=5, price=100.0) is False
    assert p.shares == 0
    assert p.cash == 100.0


def test_sell_caps_at_held_shares():
    p = Portfolio(cash=0.0, shares=3, fee=0.0, slippage=0.0)
    assert p.sell(tick=1, shares=10, price=50.0) is True
    assert p.shares == 0
    assert p.cash == 150.0


def test_sell_with_no_shares_is_noop():
    p = Portfolio(cash=0.0, shares=0)
    assert p.sell(tick=1, shares=5, price=50.0) is False


def test_equity_marks_to_market():
    p = Portfolio(cash=500.0, shares=5)
    assert p.equity(price=100.0) == 1000.0


def test_fees_and_slippage_applied():
    p = Portfolio(cash=1000.0, fee=1.0, slippage=0.01)
    p.buy(tick=0, shares=5, price=100.0)
    # cost = 5 * 100 * 1.01 + 1 = 506
    assert abs(p.cash - 494.0) < 1e-9
