from stock_agents.core.schemas import PriceBar
from stock_agents.data.technical_analysis import analyze_price_history, calculate_sma


def test_calculate_sma_uses_last_period_values() -> None:
    assert calculate_sma([1, 2, 3, 4, 5], 3) == 4


def test_analyze_price_history_returns_overlays_and_patterns() -> None:
    bars = [
        PriceBar(
            date=f"2026-05-{index + 1:02d}",
            open=100 + index,
            high=102 + index,
            low=99 + index,
            close=101 + index,
            volume=1000,
        )
        for index in range(60)
    ]

    analysis = analyze_price_history(bars)

    assert analysis is not None
    assert analysis.trend_direction == "uptrend"
    assert analysis.support is not None
    assert analysis.resistance is not None
    assert {overlay.kind for overlay in analysis.overlays} == {"trend", "support", "resistance"}
    assert analysis.patterns
