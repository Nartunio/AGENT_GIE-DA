import re
from collections import Counter

from stock_agents.core.schemas import SocialPost, SocialSignal

POSITIVE_TERMS = {
    "beat",
    "bullish",
    "buy",
    "growth",
    "long",
    "profit",
    "record",
    "strong",
    "upgrade",
    "upside",
    "zysk",
    "wzrost",
    "kupuj",
    "mocny",
}

NEGATIVE_TERMS = {
    "bearish",
    "cut",
    "debt",
    "downgrade",
    "fall",
    "loss",
    "miss",
    "risk",
    "sell",
    "short",
    "spadek",
    "strata",
    "ryzyko",
    "sprzedaj",
    "slaby",
}

STOP_WORDS = {
    "about",
    "after",
    "and",
    "for",
    "from",
    "has",
    "into",
    "is",
    "not",
    "the",
    "this",
    "with",
    "oraz",
    "jest",
    "dla",
    "or",
    "na",
    "po",
}


def build_social_signal(platform: str, query: str, posts: list[SocialPost]) -> SocialSignal:
    if not posts:
        return SocialSignal(
            platform=platform,
            query=query,
            mention_count=0,
            sentiment_score=0.0,
            engagement_score=0.0,
            key_topics=[],
            sample_posts=[],
        )

    positive = 0
    negative = 0
    engagement = 0
    topic_counts: Counter[str] = Counter()

    for post in posts:
        text = post.text.lower()
        positive += sum(1 for term in POSITIVE_TERMS if term in text)
        negative += sum(1 for term in NEGATIVE_TERMS if term in text)
        engagement += post.like_count + post.repost_count * 2 + post.reply_count + post.quote_count * 2
        topic_counts.update(_keywords(text))

    raw_sentiment = (positive - negative) / max(positive + negative, 1)
    return SocialSignal(
        platform=platform,
        query=query,
        mention_count=len(posts),
        sentiment_score=max(-1.0, min(1.0, raw_sentiment)),
        engagement_score=float(engagement),
        key_topics=[topic for topic, _ in topic_counts.most_common(6)],
        sample_posts=posts[:5],
    )


def _keywords(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z0-9_ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]{4,}", text.lower())
    return [word for word in words if word not in STOP_WORDS and not word.startswith("http")]
