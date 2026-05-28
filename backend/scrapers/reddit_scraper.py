"""
Reddit scraper using PRAW with script-type app credentials.
"""
import praw
import os
import time
import random
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

FASHION_SUBREDDITS = [
    "femalefashionadvice",
    "malefashionadvice",
    "streetwear",
    "ThriftStoreHauls",
    "VintageFashion",
    "cottagecore",
    "darkacademia",
    "capsulewardrobe",
    "femalefashion",
]

TREND_KEYWORDS = [
    "aesthetic", "core", "trend", "wearing", "obsessed", "everyone is",
    "suddenly", "blew up", "going mainstream", "style", "outfit",
    "fashion", "vibes", "micro trend", "having a moment",
]


def get_reddit_client():
    return praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent="FashionFuturesMarket/0.1 (trend research tool)",
    )


def scrape_subreddit(reddit, subreddit: str, limit: int = 50) -> list[dict]:
    try:
        results = []
        for post in reddit.subreddit(subreddit).hot(limit=limit):
            title = post.title
            if any(kw in title.lower() for kw in TREND_KEYWORDS) and post.score > 30:
                results.append({
                    "title": title,
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "url": f"https://reddit.com{post.permalink}",
                    "subreddit": subreddit,
                    "source": "reddit",
                })
        return results
    except Exception as e:
        print(f"[reddit_scraper] r/{subreddit} error: {e}")
        return []


def run_reddit_scrape() -> list[dict]:
    reddit = get_reddit_client()
    all_signals = []
    for sub in FASHION_SUBREDDITS:
        signals = scrape_subreddit(reddit, sub)
        print(f"[reddit_scraper] r/{sub}: {len(signals)} signals")
        all_signals.extend(signals)
        time.sleep(random.uniform(1.0, 2.5))
    return all_signals
