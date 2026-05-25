import httpx
import pytest

from stock_agents.core.schemas import MarketSnapshot
from stock_agents.data.stooq_provider import (
    StooqMarketDataProvider,
    calculate_rsi,
    parse_stooq_csv,
)


SAMPLE_CSV = """Date,Open,High,Low,Close,Volume
2026-05-01,100,105,99,104,1200
2026-05-02,104,106,101,102,900
2026-05-03,102,109,102,108,1400
"""


def test_parse_stooq_csv() -> None:
    rows = parse_stooq_csv(SAMPLE_CSV)

    assert rows[0]["date"] == "2026-05-01"
    assert rows[-1]["close"] == 108
    assert rows[-1]["volume"] == 1400


def test_parse_stooq_csv_returns_empty_when_key_is_required() -> None:
    rows = parse_stooq_csv("Get your apikey:\n\n1. Open https://stooq.com/q/d/?s=aapl.us")

    assert rows == []


def test_calculate_rsi_returns_value_for_enough_closes() -> None:
    closes = [100, 101, 102, 101, 103, 104, 103, 105, 106, 108, 107, 109, 111, 110, 112]

    rsi = calculate_rsi(closes)

    assert rsi is not None
    assert 0 <= rsi <= 100


def test_stooq_provider_uses_fallback_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class FallbackProvider:
        def get_snapshot(self, symbol: str) -> MarketSnapshot:
            return MarketSnapshot(
                symbol=symbol,
                company_name="Fallback",
                currency="PLN",
                last_price=1.0,
            )

    def raise_error(*args: object, **kwargs: object) -> None:
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(httpx, "get", raise_error)
    provider = StooqMarketDataProvider(fallback_provider=FallbackProvider())

    snapshot = provider.get_snapshot("CDR")

    assert snapshot.company_name == "Fallback"


def test_stooq_provider_builds_snapshot_from_csv(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeResponse:
        text = SAMPLE_CSV

        def raise_for_status(self) -> None:
            return None

    def fake_get(*args: object, **kwargs: object) -> FakeResponse:
        return FakeResponse()

    monkeypatch.setattr(httpx, "get", fake_get)
    provider = StooqMarketDataProvider()

    snapshot = provider.get_snapshot("CDR")

    assert snapshot.symbol == "CDR"
    assert snapshot.company_name == "CD Projekt"
    assert snapshot.currency == "PLN"
    assert snapshot.last_price == 108
    assert snapshot.price_change_30d == pytest.approx(0.03846, rel=0.001)


def test_stooq_provider_sends_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    captured_params: dict[str, object] = {}

    class FakeResponse:
        text = SAMPLE_CSV

        def raise_for_status(self) -> None:
            return None

    def fake_get(*args: object, **kwargs: object) -> FakeResponse:
        captured_params.update(kwargs["params"])  # type: ignore[arg-type]
        return FakeResponse()

    monkeypatch.setattr(httpx, "get", fake_get)
    provider = StooqMarketDataProvider(api_key="test-key")

    provider.get_snapshot("AAPL")

    assert captured_params["apikey"] == "test-key"
    assert captured_params["s"] == "aapl.us"
