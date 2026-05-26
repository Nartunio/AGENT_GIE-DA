from stock_agents.agents.fundamental import FundamentalAgent
from stock_agents.agents.risk import RiskAgent
from stock_agents.agents.sentiment import SentimentAgent
from stock_agents.agents.synthesis import SynthesisAgent
from stock_agents.agents.technical import TechnicalAgent
from stock_agents.core.schemas import AnalysisRequest, AnalysisResponse, MarketSnapshot
from stock_agents.data.provider import MarketDataProvider
from stock_agents.data.social_provider import SocialDataProvider


class AnalysisOrchestrator:
    def __init__(
        self,
        market_data_provider: MarketDataProvider,
        social_data_provider: SocialDataProvider | None = None,
    ) -> None:
        self.market_data_provider = market_data_provider
        self.social_data_provider = social_data_provider
        self.agents = [
            FundamentalAgent(),
            TechnicalAgent(),
            SentimentAgent(),
            RiskAgent(),
        ]
        self.synthesis_agent = SynthesisAgent()

    def analyze(self, request: AnalysisRequest) -> AnalysisResponse:
        snapshot = self.load_snapshot(request.symbol)
        findings = [agent.analyze(snapshot, request) for agent in self.agents]
        return self.synthesis_agent.synthesize(snapshot, request, findings)

    def load_snapshot(self, symbol: str) -> MarketSnapshot:
        snapshot = self.market_data_provider.get_snapshot(symbol)
        if self.social_data_provider is None:
            return snapshot
        social_signal = self.social_data_provider.get_signal(snapshot.symbol, snapshot.company_name)
        return snapshot.model_copy(update={"social_signal": social_signal})
