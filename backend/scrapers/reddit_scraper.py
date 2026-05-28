import praw
import os
from datetime import datetime, timedelta
from collections import Counter
import re

FASHION_SUBREDDITS = [
    "femalefashionadvice",
    "malefashionadvice",
    "streetwear",
    "frugalmalefashion",
    "Flipping",
    "ThriftStoreHauls",
    "VintageFashion",
    "cottagecore",
    "darkacademia",
]

TREND_KEYWORDS = [
    "aesthetic", "core", "vibes", "style", "trend", "wearing",
    "obsessed", "everyone is", "suddenly", "blew up", "going mainstream"
]


def get_reddit_client():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent="FashionFuturesMarket/0.1",
    )


def scrape_subreddit(reddit, subreddit_name: str, days_back: int = 14) -> list[dict]:
    subreddit = reddit.subreddit(subreddit_name)
    cutoff = datetime.utcnow() - timedelta(days=days_back)
    posts = []

    for post in subreddit.hot(limit=100):
        created = datetime.utcfromtimestamp(post.created_utc)
        if created < cutoff:
            continue
        posts.append({
            "title": post.title,
            "score": post.score,
            "num_comments": post.num_comments,
            "url": post.url,
            "created_at": created.isoformat(),
            "subreddit": subreddit_name,
        })

    return posts


def extract_trend_signals(posts: list[dict]) -> list[dict]:
    """Find posts with high engagement that mention trend-related language."""
    signals = []
    for post in posts:
        text = post["title"].lower()
        if any(kw in text for kw in TREND_KEYWORDS) and post["score"] > 50:
            signals.append(post)
    return signals


def run_reddit_scrape() -> list[dict]:
    reddit = get_reddit_client()
    all_signals = []
    for sub in FASHION_SUBREDDITS:
        posts = scrape_subreddit(reddit, sub)
        signals = extract_trend_signals(posts)
        all_signals.extend(signals)
    return all_signals
