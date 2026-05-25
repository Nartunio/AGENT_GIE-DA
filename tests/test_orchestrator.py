from stock_agents.core.orchestrator import AnalysisOrchestrator
from stock_agents.core.schemas import AnalysisRequest
from stock_agents.data.mock_provider import MockMarketDataProvider


def test_orchestrator_returns_complete_analysis() -> None:
    orchestrator = AnalysisOrchestrator(MockMarketDataProvider())

    result = orchestrator.analyze(AnalysisRequest(symbol="msft"))

    assert result.symbol == "MSFT"
    assert result.findings
    assert result.thesis
    assert result.next_steps
