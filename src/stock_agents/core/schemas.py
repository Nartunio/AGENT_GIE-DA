from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class AnalysisHorizon(StrEnum):
    short = "short"
    medium = "medium"
    long = "long"


class RiskProfile(StrEnum):
    conservative = "conservative"
    balanced = "balanced"
    aggressive = "aggressive"


class Rating(StrEnum):
    avoid = "avoid"
    watch = "watch"
    neutral = "neutral"
    buy = "buy"
    strong_buy = "strong_buy"


class AnalysisRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=16, examples=["AAPL"])
    horizon: AnalysisHorizon = AnalysisHorizon.medium
    risk_profile: RiskProfile = RiskProfile.balanced

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.strip().upper()


class MarketSnapshot(BaseModel):
    symbol: str
    company_name: str
    currency: str
    last_price: float
    market_cap: float | None = None
    pe_ratio: float | None = None
    revenue_growth: float | None = None
    debt_to_equity: float | None = None
    rsi_14: float | None = None
    price_change_30d: float | None = None
    news_sentiment: float | None = None
    social_signal: "SocialSignal | None" = None


class SocialPost(BaseModel):
    platform: str
    post_id: str
    text: str
    author: str | None = None
    created_at: str | None = None
    url: str | None = None
    like_count: int = 0
    repost_count: int = 0
    reply_count: int = 0
    quote_count: int = 0


class SocialSignal(BaseModel):
    platform: str
    query: str
    mention_count: int
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    engagement_score: float = Field(ge=0.0)
    key_topics: list[str] = Field(default_factory=list)
    sample_posts: list[SocialPost] = Field(default_factory=list)


class AgentFinding(BaseModel):
    agent: str
    score: float = Field(ge=-1.0, le=1.0)
    summary: str
    evidence: list[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    symbol: str
    rating: Rating
    confidence: float = Field(ge=0.0, le=1.0)
    thesis: str
    findings: list[AgentFinding]
    risks: list[str]
    next_steps: list[str]


class HealthResponse(BaseModel):
    status: str
    environment: str
