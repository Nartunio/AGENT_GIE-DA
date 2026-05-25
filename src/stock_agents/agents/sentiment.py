from stock_agents.agents.base import AnalysisAgent
from stock_agents.core.schemas import AgentFinding, AnalysisRequest, MarketSnapshot


class SentimentAgent(AnalysisAgent):
    name = "sentiment"

    def analyze(self, snapshot: MarketSnapshot, request: AnalysisRequest) -> AgentFinding:
        sentiment = snapshot.news_sentiment
        if sentiment is None:
            return AgentFinding(
                agent=self.name,
                score=0.0,
                summary="No reliable sentiment signal is available.",
                evidence=["News sentiment provider has not been connected yet."],
            )

        score = max(-1.0, min(1.0, sentiment))
        if score > 0.15:
            evidence = ["Recent market narrative is positive."]
        elif score < -0.15:
            evidence = ["Recent market narrative is negative."]
        else:
            evidence = ["Recent market narrative is mixed."]

        return AgentFinding(
            agent=self.name,
            score=score,
            summary=f"Sentiment signal is scored at {score:.2f}.",
            evidence=evidence,
        )
