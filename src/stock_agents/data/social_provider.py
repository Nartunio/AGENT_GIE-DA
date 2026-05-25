from typing import Protocol

from stock_agents.core.schemas import SocialSignal


class SocialDataProvider(Protocol):
    def get_signal(self, symbol: str, company_name: str) -> SocialSignal:
        """Return normalized social-media signal for a company."""
