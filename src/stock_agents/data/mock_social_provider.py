from stock_agents.core.schemas import SocialPost, SocialSignal
from stock_agents.data.social_analysis import build_social_signal


class MockSocialDataProvider:
    def get_signal(self, symbol: str, company_name: str) -> SocialSignal:
        posts = [
            SocialPost(
                platform="mock-x",
                post_id=f"{symbol}-1",
                author="market_observer",
                text=f"{company_name} shows strong growth momentum and improving profit quality.",
                like_count=42,
                repost_count=8,
                reply_count=5,
            ),
            SocialPost(
                platform="mock-x",
                post_id=f"{symbol}-2",
                author="risk_watch",
                text=f"Investors still debate valuation risk around {symbol} after the recent rally.",
                like_count=18,
                repost_count=3,
                reply_count=9,
            ),
        ]
        return build_social_signal(platform="mock-x", query=company_name, posts=posts)
