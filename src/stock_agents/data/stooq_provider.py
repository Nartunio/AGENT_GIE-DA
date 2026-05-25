import csv
import io
from datetime import UTC, datetime, timedelta
from statistics import mean
from typing import Any

import httpx

from stock_agents.core.schemas import MarketSnapshot
from stock_agents.data.provider import MarketDataProvider


class StooqMarketDataProvider:
    base_url = "https://stooq.com/q/d/l/"

    symbol_aliases = {
        "AAPL": "aapl.us",
        "MSFT": "msft.us",
        "CDR": "cdr.pl",
        "CD PROJEKT": "cdr.pl",
        "PKO": "pko.pl",
        "PKO BP": "pko.pl",
        "PKN": "pkn.pl",
        "ORLEN": "pkn.pl",
    }

    company_names = {
        "aapl.us": "Apple Inc.",
        "msft.us": "Microsoft Corporation",
        "cdr.pl": "CD Projekt",
        "pko.pl": "PKO Bank Polski",
        "pkn.pl": "Orlen",
    }

    currencies = {
        ".pl": "PLN",
        ".us": "USD",
    }

    def __init__(
        self,
        api_key: str | None = None,
        fallback_provider: MarketDataProvider | None = None,
        timeout_seconds: float = 10.0,
        lookback_days: int = 120,
    ) -> None:
        self.api_key = api_key
        self.fallback_provider = fallback_provider
        self.timeout_seconds = timeout_seconds
        self.lookback_days = lookback_days

    def get_snapshot(self, symbol: str) -> MarketSnapshot:
        try:
            stooq_symbol = self._normalize_symbol(symbol)
            rows = self._fetch_daily_rows(stooq_symbol)
            if len(rows) < 2:
                raise ValueError(f"Stooq returned too few rows for {stooq_symbol}")
            return self._snapshot_from_rows(symbol, stooq_symbol, rows)
        except Exception:
            if self.fallback_provider is None:
                raise
            return self.fallback_provider.get_snapshot(symbol)

    def _fetch_daily_rows(self, stooq_symbol: str) -> list[dict[str, Any]]:
        end = datetime.now(UTC).date()
        start = end - timedelta(days=self.lookback_days)
        params = {
            "s": stooq_symbol,
            "d1": start.strftime("%Y%m%d"),
            "d2": end.strftime("%Y%m%d"),
            "i": "d",
        }
        if self.api_key:
            params["apikey"] = self.api_key

        response = httpx.get(
            self.base_url,
            params=params,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        return parse_stooq_csv(response.text)

    @classmethod
    def _normalize_symbol(cls, symbol: str) -> str:
        normalized = symbol.strip().upper()
        if normalized in cls.symbol_aliases:
            return cls.symbol_aliases[normalized]
        if "." in normalized:
            return normalized.lower()
        return f"{normalized.lower()}.pl"

    def _snapshot_from_rows(
        self,
        requested_symbol: str,
        stooq_symbol: str,
        rows: list[dict[str, Any]],
    ) -> MarketSnapshot:
        latest = rows[-1]
        comparison = rows[-22] if len(rows) >= 22 else rows[0]
        closes = [row["close"] for row in rows]
        last_price = latest["close"]
        comparison_price = comparison["close"]
        price_change_30d = (
            (last_price - comparison_price) / comparison_price if comparison_price else None
        )

        return MarketSnapshot(
            symbol=requested_symbol.strip().upper(),
            company_name=self.company_names.get(stooq_symbol, requested_symbol.strip().upper()),
            currency=self._currency_for(stooq_symbol),
            last_price=last_price,
            market_cap=None,
            pe_ratio=None,
            revenue_growth=None,
            debt_to_equity=None,
            rsi_14=calculate_rsi(closes),
            price_change_30d=price_change_30d,
            news_sentiment=None,
        )

    @classmethod
    def _currency_for(cls, stooq_symbol: str) -> str:
        for suffix, currency in cls.currencies.items():
            if stooq_symbol.endswith(suffix):
                return currency
        return "USD"


def parse_stooq_csv(csv_text: str) -> list[dict[str, Any]]:
    cleaned = csv_text.strip()
    if not cleaned or cleaned.lower().startswith("get your apikey"):
        return []

    reader = csv.DictReader(io.StringIO(cleaned))
    rows: list[dict[str, Any]] = []
    for row in reader:
        if not row or row.get("Close") in {None, "", "N/D"}:
            continue
        rows.append(
            {
                "date": row["Date"],
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(float(row.get("Volume") or 0)),
            }
        )
    return rows


def calculate_rsi(closes: list[float], period: int = 14) -> float | None:
    if len(closes) <= period:
        return None

    deltas = [current - previous for previous, current in zip(closes, closes[1:], strict=False)]
    recent = deltas[-period:]
    gains = [delta for delta in recent if delta > 0]
    losses = [-delta for delta in recent if delta < 0]
    average_gain = mean(gains) if gains else 0
    average_loss = mean(losses) if losses else 0

    if average_loss == 0:
        return 100.0 if average_gain > 0 else 50.0

    relative_strength = average_gain / average_loss
    return round(100 - (100 / (1 + relative_strength)), 2)
