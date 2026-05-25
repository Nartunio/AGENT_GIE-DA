from stock_agents.agents.base import AnalysisAgent
from stock_agents.core.schemas import AgentFinding, AnalysisRequest, MarketSnapshot


class FundamentalAgent(AnalysisAgent):
    name = "fundamental"

    def analyze(self, snapshot: MarketSnapshot, request: AnalysisRequest) -> AgentFinding:
        score = 0.0
        evidence: list[str] = []

        if snapshot.revenue_growth is not None:
            if snapshot.revenue_growth > 0.10:
                score += 0.35
                evidence.append("Revenue growth is above 10%.")
            elif snapshot.revenue_growth < 0:
                score -= 0.35
                evidence.append("Revenue is shrinking.")

        if snapshot.pe_ratio is not None:
            if snapshot.pe_ratio < 20:
                score += 0.25
                evidence.append("Valuation multiple is moderate.")
            elif snapshot.pe_ratio > 35:
                score -= 0.25
                evidence.append("Valuation multiple is elevated.")

        if snapshot.debt_to_equity is not None:
            if snapshot.debt_to_equity < 1.0:
                score += 0.20
                evidence.append("Balance-sheet leverage is contained.")
            elif snapshot.debt_to_equity > 2.0:
                score -= 0.25
                evidence.append("Balance-sheet leverage is high.")

        score = max(-1.0, min(1.0, score))
        return AgentFinding(
            agent=self.name,
            score=score,
            summary=f"Fundamental profile for {snapshot.company_name} is scored at {score:.2f}.",
            evidence=evidence or ["Insufficient fundamental data for a strong view."],
        )
