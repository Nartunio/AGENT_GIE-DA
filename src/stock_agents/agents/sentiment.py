from stock_agents.agents.base import AnalysisAgent
from stock_agents.core.schemas import AgentFinding, AnalysisRequest, MarketSnapshot


class SentimentAgent(AnalysisAgent):
    name = "sentiment"

    def analyze(self, snapshot: MarketSnapshot, request: AnalysisRequest) -> AgentFinding:
        social_signal = snapshot.social_signal
        if social_signal is None and snapshot.news_sentiment is None:
            return AgentFinding(
                agent=self.name,
                score=0.0,
                summary="No reliable sentiment signal is available.",
                evidence=["News sentiment provider has not been connected yet."],
            )

        social_sentiment = social_signal.sentiment_score if social_signal else 0.0
        news_sentiment = snapshot.news_sentiment if snapshot.news_sentiment is not None else social_sentiment
        score = max(-1.0, min(1.0, (news_sentiment + social_sentiment) / 2))

        if score > 0.15:
            evidence = ["Recent market narrative is positive."]
        elif score < -0.15:
            evidence = ["Recent market narrative is negative."]
        else:
            evidence = ["Recent market narrative is mixed."]

        if social_signal is not None:
            evidence.append(
                f"{social_signal.platform} mentions: {social_signal.mention_count}, "
                f"engagement score: {social_signal.engagement_score:.0f}."
            )
            if social_signal.key_topics:
                evidence.append("Social topics: " + ", ".join(social_signal.key_topics[:4]) + ".")
            if social_signal.sample_posts:
                evidence.append(f"Sample post: {social_signal.sample_posts[0].text[:160]}")

        return AgentFinding(
            agent=self.name,
            score=score,
            summary=f"Sentiment signal is scored at {score:.2f}.",
            evidence=evidence,
        )
