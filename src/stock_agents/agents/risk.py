from stock_agents.agents.base import AnalysisAgent
from stock_agents.core.schemas import AgentFinding, AnalysisRequest, MarketSnapshot


class RiskAgent(AnalysisAgent):
    name = "risk"

    def analyze(self, snapshot: MarketSnapshot, request: AnalysisRequest) -> AgentFinding:
        risk_penalty = 0.0
        evidence: list[str] = []

        if snapshot.debt_to_equity is not None and snapshot.debt_to_equity > 2.0:
            risk_penalty -= 0.35
            evidence.append("High leverage increases downside sensitivity.")

        if snapshot.pe_ratio is not None and snapshot.pe_ratio > 40:
            risk_penalty -= 0.25
            evidence.append("High valuation reduces margin of safety.")

        if request.risk_profile == "conservative":
            risk_penalty -= 0.10
            evidence.append("Conservative risk profile requires a higher hurdle.")

        score = max(-1.0, min(1.0, risk_penalty))
        return AgentFinding(
            agent=self.name,
            score=score,
            summary=f"Risk profile is scored at {score:.2f}.",
            evidence=evidence or ["No major placeholder risk signal was detected."],
        )
