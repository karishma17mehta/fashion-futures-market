"""
Reddit fashion trend scraper using PRAW.
Filters for posts that are actually discussing trends — not outfit photos,
random questions, or low-engagement posts.

Signal quality tiers:
    STRONG  — explicit trend discussion (micro trend, aesthetic, blew up, etc.)
    MEDIUM  — style/fashion discussion with good engagement
    WEAK    — general fashion content — excluded from pipeline

Only STRONG signals are returned. Minimum score thresholds are higher
than before to ensure we're capturing real community signals, not noise.
"""
import os
import random
import re
import time
from pathlib import Path

import praw
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

FASHION_SUBREDDITS: list[str] = [
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

# ── Signal filters ─────────────────────────────────────────────────────────────

# STRONG: explicit trend vocabulary — these posts are discussing trends
STRONG_KEYWORDS: list[str] = [
    "micro trend", "microtrend", "aesthetic", "blew up", "going viral",
    "everyone is wearing", "suddenly everywhere", "having a moment",
    "comeback", "revival", "going mainstream", "trend report", "trend alert",
    "trend watch", "trending", "what's trending", "new aesthetic",
    "core", "old money", "quiet luxury", "coquette", "dark academia",
    "cottagecore", "gorpcore", "balletcore", "streetwear trend",
    "fashion trend", "style trend", "this trend", "that trend",
    "blew up on tiktok", "went viral", "tiktok made me",
    "is this a trend", "noticed a trend", "emerging trend",
    "about to be everywhere", "getting popular", "taking off",
]

# NOISE: things that look like trend discussions but aren't
NOISE_PATTERNS: list[str] = [
    r"^(my|today'?s?|this|rate my|first|help|iso|wtb|wts|wtt|lf|looking for)",
    r"^(found|scored|thrifted|bought|got|picked up|just got|just bought)",
    r"(cake|food|recipe|baking|garden|plant|flower|room|bedroom|library|phone|background|comic|art)",
    r"(for \$\d|\$\d+ )",
    r"^(what.*(wear|should|do|think|recommend|suggest))",
    r"^(where.*(find|buy|get|cop))",
    r"(outfit.*(inspo|idea|help|check|post|today|share))",
    r"(how do (i|you|we))",
    r"^(does anyone|can anyone|would anyone)",
    r"(photos?|photo shoot|photoshoot)",
    r"(for sale|selling|shop|store|brand|haul)",
]

# Minimum upvote scores per subreddit type
_MIN_SCORES: dict[str, int] = {
    "femalefashionadvice": 200,
    "malefashionadvice":   200,
    "streetwear":          150,
    "ThriftStoreHauls":    100,
    "VintageFashion":       80,
    "cottagecore":          60,
    "darkacademia":         60,
    "capsulewardrobe":      80,
    "femalefashion":        80,
}
_DEFAULT_MIN_SCORE = 100


def _is_strong_signal(title: str, score: int, subreddit: str) -> bool:
    """Return True only if this post is genuinely discussing a trend."""
    title_lower = title.lower()

    # Must meet upvote threshold for its subreddit
    min_score = _MIN_SCORES.get(subreddit, _DEFAULT_MIN_SCORE)
    if score < min_score:
        return False

    # Must not match noise patterns
    for pattern in NOISE_PATTERNS:
        if re.search(pattern, title_lower):
            return False

    # Must contain at least one strong trend keyword
    return any(kw in title_lower for kw in STRONG_KEYWORDS)


def _extract_trend_name(title: str) -> str:
    """
    Try to extract the trend name from a post title for cleaner signal naming.
    e.g. "The 'coastal grandmother' aesthetic is having a moment" → "coastal grandmother"
    """
    # Look for quoted terms
    quoted = re.findall(r"['\"]([^'\"]{4,40})['\"]", title)
    if quoted:
        return quoted[0]
    # Look for "X aesthetic", "X core", "X style", "X trend"
    pattern = re.search(
        r"([\w\s]{3,30})\s+(aesthetic|core|style|trend|look|vibes?)",
        title, re.IGNORECASE
    )
    if pattern:
        return pattern.group(0).strip()
    return title


def get_reddit_client() -> praw.Reddit:
    return praw.Reddit(
        client_id     = os.getenv("REDDIT_CLIENT_ID"),
        client_secret = os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent    = "FashionFuturesMarket/0.1 (trend research tool)",
    )


def scrape_subreddit(reddit: praw.Reddit, subreddit: str, limit: int = 100) -> list[dict]:
    """Scrape hot posts from one subreddit, returning only strong trend signals."""
    try:
        results = []
        for post in reddit.subreddit(subreddit).hot(limit=limit):
            if not _is_strong_signal(post.title, post.score, subreddit):
                continue

            trend_name = _extract_trend_name(post.title)
            results.append({
                "title":        trend_name,
                "description":  post.title,   # full title as context
                "score":        post.score,
                "num_comments": post.num_comments,
                "url":          f"https://reddit.com{post.permalink}",
                "subreddit":    subreddit,
                "source":       "reddit",
            })
        return results
    except Exception as e:
        print(f"[reddit_scraper] r/{subreddit} error: {e}")
        return []


def run_reddit_scrape() -> list[dict]:
    reddit = get_reddit_client()
    all_signals: list[dict] = []
    for sub in FASHION_SUBREDDITS:
        signals = scrape_subreddit(reddit, sub)
        print(f"[reddit_scraper] r/{sub}: {len(signals)} strong trend signals")
        all_signals.extend(signals)
        time.sleep(random.uniform(0.8, 2.0))
    return all_signals


if __name__ == "__main__":
    signals = run_reddit_scrape()
    print(f"\nTotal: {len(signals)} strong signals")
    for s in signals:
        print(f"  [{s['score']:>5} pts] r/{s['subreddit']}: {s['description'][:70]}")
