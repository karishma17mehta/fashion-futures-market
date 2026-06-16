"""
World News API scraper
======================
Pulls recent fashion / style news as trend signals.

Why this source: unlike Google Trends / Reddit scraping (which get rate-limited
or IP-blocked from cloud servers), this is a proper API — it runs fine from
Railway's cloud cron and gives broad, fresh, dated editorial coverage.

Each article becomes an editorial-style signal. Claude's narrative step later
distills the actual trend name from the headline/text, so we don't need an
extra extraction call here.

Set WORLD_NEWS_API_KEY in the environment. If it's missing, this no-ops
(returns []), so the pipeline keeps working without it.

Docs: https://worldnewsapi.com/docs/
"""
import os
from datetime import datetime, timedelta

import httpx

API_URL = "https://api.worldnewsapi.com/search-news"

# Focused fashion queries. Kept small to respect the points budget
# (each search costs API points). Broaden later if coverage is thin.
QUERIES = [
    "fashion trend",
    "style trend OR viral fashion",
    "new collection OR runway trend",
]

# Generic news words that aren't trends — used to drop obvious noise.
_NOISE = {
    "stock", "earnings", "lawsuit", "merger", "acquisition", "ceo steps",
    "quarterly", "ipo", "layoffs",
}


def _looks_fashion(title: str, text: str) -> bool:
    blob = f"{title} {text}".lower()
    if any(n in blob for n in _NOISE):
        return False
    # Require at least one fashion-y anchor word
    anchors = ("fashion", "style", "trend", "wear", "outfit", "runway",
               "collection", "aesthetic", "wardrobe", "designer", "look")
    return any(a in blob for a in anchors)


def scrape(days_back: int = 7, per_query: int = 12) -> list[dict]:
    api_key = os.getenv("WORLD_NEWS_API_KEY")
    if not api_key:
        print("     [world_news] WORLD_NEWS_API_KEY not set — skipping")
        return []

    earliest = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    signals: list[dict] = []
    seen_titles: set[str] = set()

    for q in QUERIES:
        try:
            resp = httpx.get(
                API_URL,
                params={
                    "api-key": api_key,
                    "text": q,
                    "language": "en",
                    "earliest-publish-date": earliest,
                    "number": per_query,
                    "sort": "publish-time",
                    "sort-direction": "DESC",
                },
                timeout=30,
            )
            resp.raise_for_status()
            articles = resp.json().get("news", []) or []
        except Exception as e:
            print(f"     [world_news] query '{q}' failed: {e}")
            continue

        for a in articles:
            title = (a.get("title") or "").strip()
            text = (a.get("text") or a.get("summary") or "").strip()
            if not title:
                continue
            key = title.lower()
            if key in seen_titles:
                continue
            if not _looks_fashion(title, text):
                continue
            seen_titles.add(key)

            signals.append({
                "source": "world_news",
                "title": title,
                "description": text[:600],
                "url": a.get("url", ""),
                "keywords": [],                 # narrative step extracts the trend
                "published": a.get("publish_date", ""),
            })

    print(f"     [world_news] {len(signals)} fashion signals from {len(QUERIES)} queries")
    return signals


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    for s in scrape():
        print(f"  • {s['title']}")
