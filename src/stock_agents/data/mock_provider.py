from datetime import date, timedelta

from stock_agents.core.schemas import MarketSnapshot, PriceBar
from stock_agents.data.technical_analysis import analyze_price_history


class MockMarketDataProvider:
    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        normalized = symbol.upper()
        price_history = _generate_price_history(normalized)
        presets = {
            "AAPL": MarketSnapshot(
                symbol="AAPL",
                company_name="Apple Inc.",
                currency="USD",
                last_price=190.0,
                price_history=price_history,
                market_cap=2_900_000_000_000,
                pe_ratio=29.0,
                revenue_growth=0.06,
                debt_to_equity=1.6,
                rsi_14=54.0,
                price_change_30d=0.04,
                news_sentiment=0.18,
                technical_analysis=analyze_price_history(price_history),
            ),
            "MSFT": MarketSnapshot(
                symbol="MSFT",
                company_name="Microsoft Corporation",
                currency="USD",
                last_price=420.0,
                price_history=price_history,
                market_cap=3_100_000_000_000,
                pe_ratio=34.0,
                revenue_growth=0.14,
                debt_to_equity=0.4,
                rsi_14=61.0,
                price_change_30d=0.08,
                news_sentiment=0.24,
                technical_analysis=analyze_price_history(price_history),
            ),
        }
        return presets.get(
            normalized,
            MarketSnapshot(
                symbol=normalized,
                company_name=f"{normalized} placeholder company",
                currency="USD",
                last_price=100.0,
                price_history=price_history,
                market_cap=None,
                pe_ratio=25.0,
                revenue_growth=0.05,
                debt_to_equity=1.0,
                rsi_14=50.0,
                price_change_30d=0.0,
                news_sentiment=0.0,
                technical_analysis=analyze_price_history(price_history),
            ),
        )


def _generate_price_history(symbol: str, length: int = 80) -> list[PriceBar]:
    seed = sum(ord(char) for char in symbol)
    base = 70 + seed % 140
    drift = ((seed % 13) - 4) / 220
    today = date.today()
    bars: list[PriceBar] = []
    close = float(base)

    for index in range(length):
        wave = ((index % 9) - 4) * 0.006
        close = max(1.0, close * (1 + drift + wave))
        open_price = close * (1 - wave / 2)
        high = max(open_price, close) * 1.012
        low = min(open_price, close) * 0.988
        bars.append(
            PriceBar(
                date=(today - timedelta(days=length - index)).isoformat(),
                open=round(open_price, 2),
                high=round(high, 2),
                low=round(low, 2),
                close=round(close, 2),
                volume=100_000 + ((seed + index * 7919) % 900_000),
            )
        )

    return bars
