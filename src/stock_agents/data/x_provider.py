from typing import Any

import httpx

from stock_agents.core.schemas import SocialPost, SocialSignal
from stock_agents.data.social_analysis import build_social_signal


class XRecentSearchProvider:
    base_url = "https://api.x.com/2/tweets/search/recent"

    def __init__(
        self,
        bearer_token: str,
        max_results: int = 20,
        timeout_seconds: float = 10.0,
    ) -> None:
        self.bearer_token = bearer_token
        self.max_results = max(10, min(max_results, 100))
        self.timeout_seconds = timeout_seconds

    def get_signal(self, symbol: str, company_name: str) -> SocialSignal:
        query = self._build_query(symbol, company_name)
        response = httpx.get(
            self.base_url,
            headers={"Authorization": f"Bearer {self.bearer_token}"},
            params={
                "query": query,
                "max_results": self.max_results,
                "tweet.fields": "created_at,author_id,public_metrics",
                "expansions": "author_id",
                "user.fields": "username,name",
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        posts = self._parse_posts(payload)
        return build_social_signal(platform="x", query=query, posts=posts)

    @staticmethod
    def _build_query(symbol: str, company_name: str) -> str:
        normalized_symbol = symbol.upper()
        terms = [f'"{company_name}"', f"${normalized_symbol}", normalized_symbol]
        return f"({' OR '.join(terms)}) lang:en -is:retweet"

    @staticmethod
    def _parse_posts(payload: dict[str, Any]) -> list[SocialPost]:
        users = {
            user["id"]: user.get("username") or user.get("name")
            for user in payload.get("includes", {}).get("users", [])
            if "id" in user
        }
        posts: list[SocialPost] = []

        for item in payload.get("data", []):
            metrics = item.get("public_metrics", {})
            post_id = item["id"]
            author = users.get(item.get("author_id"))
            posts.append(
                SocialPost(
                    platform="x",
                    post_id=post_id,
                    author=author,
                    text=item.get("text", ""),
                    created_at=item.get("created_at"),
                    url=f"https://x.com/{author}/status/{post_id}" if author else None,
                    like_count=metrics.get("like_count", 0),
                    repost_count=metrics.get("retweet_count", 0),
                    reply_count=metrics.get("reply_count", 0),
                    quote_count=metrics.get("quote_count", 0),
                )
            )

        return posts
