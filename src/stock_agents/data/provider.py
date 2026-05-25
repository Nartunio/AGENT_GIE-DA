from typing import Protocol

from stock_agents.core.schemas import MarketSnapshot


class MarketDataProvider(Protocol):
    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        """Return a normalized market snapshot for a stock symbol."""
