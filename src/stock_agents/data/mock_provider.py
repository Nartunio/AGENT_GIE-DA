from stock_agents.core.schemas import MarketSnapshot


class MockMarketDataProvider:
    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        normalized = symbol.upper()
        presets = {
            "AAPL": MarketSnapshot(
                symbol="AAPL",
                company_name="Apple Inc.",
                currency="USD",
                last_price=190.0,
                market_cap=2_900_000_000_000,
                pe_ratio=29.0,
                revenue_growth=0.06,
                debt_to_equity=1.6,
                rsi_14=54.0,
                price_change_30d=0.04,
                news_sentiment=0.18,
            ),
            "MSFT": MarketSnapshot(
                symbol="MSFT",
                company_name="Microsoft Corporation",
                currency="USD",
                last_price=420.0,
                market_cap=3_100_000_000_000,
                pe_ratio=34.0,
                revenue_growth=0.14,
                debt_to_equity=0.4,
                rsi_14=61.0,
                price_change_30d=0.08,
                news_sentiment=0.24,
            ),
        }
        return presets.get(
            normalized,
            MarketSnapshot(
                symbol=normalized,
                company_name=f"{normalized} placeholder company",
                currency="USD",
                last_price=100.0,
                market_cap=None,
                pe_ratio=25.0,
                revenue_growth=0.05,
                debt_to_equity=1.0,
                rsi_14=50.0,
                price_change_30d=0.0,
                news_sentiment=0.0,
            ),
        )
