from agentic_showcase import tools


def test_sma_basic():
    assert tools.sma([1, 2, 3, 4], 2) == 3.5
    assert tools.sma([1, 2, 3], 3) == 2.0


def test_sma_insufficient_history():
    assert tools.sma([1, 2], 5) is None
    assert tools.sma([], 1) is None
    assert tools.sma([1, 2, 3], 0) is None


def test_rsi_all_gains_is_100():
    prices = [float(i) for i in range(1, 20)]
    assert tools.rsi(prices, 14) == 100.0


def test_rsi_range():
    prices = [10, 11, 10, 12, 11, 13, 12, 14, 13, 15, 14, 16, 15, 17, 16, 18]
    value = tools.rsi(prices, 14)
    assert value is not None
    assert 0.0 <= value <= 100.0


def test_volatility_of_flat_series_is_zero():
    assert tools.volatility([100.0] * 30, 20) == 0.0


def test_position_size():
    assert tools.position_size(1000, 100, 0.5) == 5
    assert tools.position_size(1000, 100, 0.0) == 0
    assert tools.position_size(0, 100, 0.5) == 0
    assert tools.position_size(1000, 0, 0.5) == 0


def test_max_drawdown():
    assert tools.max_drawdown([100, 110, 90, 95]) < 0
    assert tools.max_drawdown([100, 101, 102]) == 0.0
    assert tools.max_drawdown([]) == 0.0
    # 100 -> 50 is a 50% drawdown.
    assert abs(tools.max_drawdown([100, 50]) + 0.5) < 1e-9
