from stock_agents.core.schemas import (
    AgentFinding,
    AnalysisRequest,
    AnalysisResponse,
    MarketSnapshot,
    Rating,
)


class SynthesisAgent:
    name = "synthesis"

    def synthesize(
        self,
        snapshot: MarketSnapshot,
        request: AnalysisRequest,
        findings: list[AgentFinding],
    ) -> AnalysisResponse:
        aggregate_score = sum(finding.score for finding in findings) / max(len(findings), 1)
        rating = self._rating_from_score(aggregate_score)
        confidence = min(0.95, 0.45 + abs(aggregate_score) * 0.5)

        risks = [
            evidence
            for finding in findings
            if finding.agent == "risk" or finding.score < -0.1
            for evidence in finding.evidence
        ]

        thesis = (
            f"{snapshot.company_name} ({snapshot.symbol}) receives a {rating.value} rating "
            f"for a {request.horizon.value}-term horizon based on the current agent mix."
        )

        return AnalysisResponse(
            symbol=snapshot.symbol,
            rating=rating,
            confidence=round(confidence, 2),
            thesis=thesis,
            findings=findings,
            risks=risks or ["No explicit risk was identified by the placeholder agents."],
            next_steps=[
                "Connect a real market-data provider.",
                "Add LLM-backed qualitative analysis.",
                "Review output before using it in any investment workflow.",
            ],
        )

    @staticmethod
    def _rating_from_score(score: float) -> Rating:
        if score >= 0.45:
            return Rating.strong_buy
        if score >= 0.20:
            return Rating.buy
        if score > -0.10:
            return Rating.neutral
        if score > -0.35:
            return Rating.watch
        return Rating.avoid
