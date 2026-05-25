from stock_agents.core.schemas import SocialPost
from stock_agents.data.social_analysis import build_social_signal
from stock_agents.data.x_provider import XRecentSearchProvider


def test_social_signal_scores_posts_and_topics() -> None:
    posts = [
        SocialPost(
            platform="x",
            post_id="1",
            text="Strong growth and profit beat for ACME stock",
            like_count=10,
            repost_count=2,
        ),
        SocialPost(
            platform="x",
            post_id="2",
            text="Valuation risk and debt debate after rally",
            reply_count=3,
        ),
    ]

    signal = build_social_signal("x", "ACME", posts)

    assert signal.mention_count == 2
    assert signal.engagement_score == 17
    assert "growth" in signal.key_topics
    assert signal.sample_posts[0].post_id == "1"


def test_x_provider_parses_recent_search_payload() -> None:
    payload = {
        "data": [
            {
                "id": "123",
                "author_id": "u1",
                "text": "ACME bullish growth setup",
                "created_at": "2026-05-25T12:00:00Z",
                "public_metrics": {
                    "like_count": 5,
                    "retweet_count": 2,
                    "reply_count": 1,
                    "quote_count": 1,
                },
            }
        ],
        "includes": {"users": [{"id": "u1", "username": "analyst"}]},
    }

    posts = XRecentSearchProvider._parse_posts(payload)

    assert posts[0].author == "analyst"
    assert posts[0].url == "https://x.com/analyst/status/123"
    assert posts[0].repost_count == 2
