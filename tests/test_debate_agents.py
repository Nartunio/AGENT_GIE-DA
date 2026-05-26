from stock_agents.agents.debate import OllamaDebateOrchestrator, parse_debate_output
from stock_agents.core.orchestrator import AnalysisOrchestrator
from stock_agents.core.schemas import DebateRequest
from stock_agents.data.mock_provider import MockMarketDataProvider
from stock_agents.data.mock_social_provider import MockSocialDataProvider


class FakeOllamaClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def generate(self, model: str, prompt: str, system: str | None = None) -> str:
        self.calls.append((model, prompt))
        if "Compare both cases" in prompt:
            return """THESIS: Bear case is more evidence-sensitive, but buy case remains plausible.
DECISION: WATCH
CONFIDENCE: 0.63
ARGUMENTS:
- The technical setup is constructive but valuation data is incomplete.
- Social sentiment supports interest, not intrinsic value.
COMPARISON:
- Bull case used trend and sentiment better.
- Bear case exposed missing valuation evidence better.
REBUTTALS:
- Bull did not solve valuation uncertainty.
- Bear did not disprove momentum.
MISSING_INFORMATION:
- Full income statement.
- Peer valuation table.
"""
        if "DO-NOT-BUY" in prompt:
            return """THESIS: Do not buy without better valuation evidence.
ARGUMENTS:
- P/E and free cash flow context are incomplete.
- Momentum can reverse near resistance.
REBUTTALS:
- Bull case overweights social sentiment.
EVIDENCE_REQUESTS:
- Cash flow history.
"""
        return """THESIS: Buy case is supported by momentum and improving narrative.
ARGUMENTS:
- Trend is positive.
- Social sentiment is supportive.
REBUTTALS:
- Valuation risk should be sized, not ignored.
EVIDENCE_REQUESTS:
- Peer multiples.
"""


def test_parse_debate_output_extracts_sections() -> None:
    raw = """THESIS: Buy with discipline.
ARGUMENTS:
- Strong trend.
- Positive sentiment.
REBUTTALS:
- Valuation risk is manageable.
EVIDENCE_REQUESTS:
- Updated earnings.
"""

    output = parse_debate_output("bull", "model", raw)

    assert output.thesis == "Buy with discipline."
    assert output.arguments == ["Strong trend.", "Positive sentiment."]
    assert output.rebuttals == ["Valuation risk is manageable."]


def test_ollama_debate_orchestrator_runs_three_roles() -> None:
    base = AnalysisOrchestrator(MockMarketDataProvider(), MockSocialDataProvider())
    client = FakeOllamaClient()
    debate = OllamaDebateOrchestrator(
        ollama_client=client,  # type: ignore[arg-type]
        snapshot_loader=base.load_snapshot,
        base_analyzer=base.analyze,
        bull_model="bull-model",
        bear_model="bear-model",
        judge_model="judge-model",
    )

    response = debate.debate(DebateRequest(symbol="AAPL", rounds=1))

    assert response.final_decision == "WATCH"
    assert response.confidence == 0.63
    assert response.bull_case.role == "bull"
    assert response.bear_case.role == "bear"
    assert response.judge.role == "judge"
    assert [call[0] for call in client.calls] == ["bull-model", "bear-model", "judge-model"]
