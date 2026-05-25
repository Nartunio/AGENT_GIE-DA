from stock_agents.core.schemas import (
    ChartOverlay,
    PriceBar,
    TechnicalAnalysis,
    TechnicalPattern,
)


def analyze_price_history(bars: list[PriceBar]) -> TechnicalAnalysis | None:
    if len(bars) < 5:
        return None

    closes = [bar.close for bar in bars]
    highs = [bar.high for bar in bars]
    lows = [bar.low for bar in bars]
    support = min(lows[-20:]) if len(lows) >= 20 else min(lows)
    resistance = max(highs[-20:]) if len(highs) >= 20 else max(highs)
    sma_short = calculate_sma(closes, 20)
    sma_long = calculate_sma(closes, 50)
    trend = _trend_direction(closes)
    overlays = _build_overlays(closes, support, resistance)
    patterns = _detect_patterns(closes, support, resistance, sma_short, sma_long)

    return TechnicalAnalysis(
        trend_direction=trend,
        support=round(support, 4),
        resistance=round(resistance, 4),
        sma_short=round(sma_short, 4) if sma_short is not None else None,
        sma_long=round(sma_long, 4) if sma_long is not None else None,
        overlays=overlays,
        patterns=patterns,
    )


def calculate_sma(values: list[float], period: int) -> float | None:
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def _trend_direction(closes: list[float]) -> str:
    window = closes[-30:] if len(closes) >= 30 else closes
    first = window[0]
    last = window[-1]
    if first == 0:
        return "sideways"
    change = (last - first) / first
    if change > 0.05:
        return "uptrend"
    if change < -0.05:
        return "downtrend"
    return "sideways"


def _build_overlays(closes: list[float], support: float, resistance: float) -> list[ChartOverlay]:
    end_index = len(closes) - 1
    start_index = max(0, end_index - 29)
    return [
        ChartOverlay(
            name="Trend line",
            kind="trend",
            start_index=start_index,
            end_index=end_index,
            start_value=round(closes[start_index], 4),
            end_value=round(closes[end_index], 4),
        ),
        ChartOverlay(
            name="Support",
            kind="support",
            start_index=start_index,
            end_index=end_index,
            start_value=round(support, 4),
            end_value=round(support, 4),
        ),
        ChartOverlay(
            name="Resistance",
            kind="resistance",
            start_index=start_index,
            end_index=end_index,
            start_value=round(resistance, 4),
            end_value=round(resistance, 4),
        ),
    ]


def _detect_patterns(
    closes: list[float],
    support: float,
    resistance: float,
    sma_short: float | None,
    sma_long: float | None,
) -> list[TechnicalPattern]:
    patterns: list[TechnicalPattern] = []
    last = closes[-1]
    range_width = max(resistance - support, 0.0001)

    if (resistance - last) / range_width < 0.15:
        patterns.append(
            TechnicalPattern(
                name="Resistance test",
                direction="watch_breakout",
                confidence=0.68,
                description="Price is close to recent resistance; breakout or rejection is likely to matter.",
            )
        )

    if (last - support) / range_width < 0.15:
        patterns.append(
            TechnicalPattern(
                name="Support test",
                direction="watch_reversal",
                confidence=0.66,
                description="Price is close to recent support; breakdown risk should be monitored.",
            )
        )

    if sma_short is not None and sma_long is not None:
        if sma_short > sma_long and last > sma_short:
            patterns.append(
                TechnicalPattern(
                    name="Moving-average alignment",
                    direction="bullish",
                    confidence=0.72,
                    description="Short moving average is above long moving average and price trades above both.",
                )
            )
        elif sma_short < sma_long and last < sma_short:
            patterns.append(
                TechnicalPattern(
                    name="Moving-average pressure",
                    direction="bearish",
                    confidence=0.72,
                    description="Short moving average is below long moving average and price trades below both.",
                )
            )

    if len(closes) >= 12:
        recent_highs = sorted(closes[-12:])[-2:]
        if abs(recent_highs[0] - recent_highs[1]) / max(recent_highs[1], 0.0001) < 0.015:
            patterns.append(
                TechnicalPattern(
                    name="Potential double top",
                    direction="bearish",
                    confidence=0.55,
                    description="Two recent highs are close together; failed breakout may signal distribution.",
                )
            )

    return patterns
