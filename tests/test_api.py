from fastapi.testclient import TestClient

from stock_agents.api.app import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_endpoint() -> None:
    response = client.post(
        "/api/v1/analyze",
        json={"symbol": "aapl", "horizon": "medium", "risk_profile": "balanced"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["symbol"] == "AAPL"
    assert body["findings"]
