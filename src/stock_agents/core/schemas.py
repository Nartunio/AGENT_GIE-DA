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
