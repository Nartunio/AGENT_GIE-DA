from stock_agents.agents.base import AnalysisAgent
from stock_agents.core.schemas import AgentFinding, AnalysisRequest, MarketSnapshot


class TechnicalAgent(AnalysisAgent):
    name = "technical"

    def analyze(self, snapshot: MarketSnapshot, request: AnalysisRequest) -> AgentFinding:
        score = 0.0
        evidence: list[str] = []

        if snapshot.price_change_30d is not None:
            if snapshot.price_change_30d > 0.05:
                score += 0.35
                evidence.append("Thirty-day price trend is positive.")
            elif snapshot.price_change_30d < -0.05:
                score -= 0.35
                evidence.append("Thirty-day price trend is negative.")

        if snapshot.rsi_14 is not None:
            if snapshot.rsi_14 < 30:
                score += 0.15
                evidence.append("RSI suggests oversold conditions.")
            elif snapshot.rsi_14 > 70:
                score -= 0.15
                evidence.append("RSI suggests overbought conditions.")

        score = max(-1.0, min(1.0, score))
        return AgentFinding(
            agent=self.name,
            score=score,
            summary=f"Technical setup is scored at {score:.2f}.",
            evidence=evidence or ["Insufficient technical data for a strong view."],
        )
