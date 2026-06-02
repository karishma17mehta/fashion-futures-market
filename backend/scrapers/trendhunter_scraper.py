"""
Fashion Editorial RSS Scraper
==============================
Replaces the defunct TrendHunter scraper (blocked with 403).
Pulls current fashion editorial content from Vogue, Harper's Bazaar, and WWD
via their public RSS feeds — all returning 2026 content.

Sources:
    Vogue Fashion    — runway, style, trend coverage
    Vogue Shopping   — product/trend feature stories
    Harper's Bazaar  — editorial trend analysis
    WWD              — industry/trade fashion news

Returns signal dicts compatible with the existing pipeline.
Each article headline + description is treated as a weak trend signal,
scored at 0% data completeness (no numeric data) — these are qualitative
signals that confirm or suggest trends rather than measure them.
"""
import random
import time
from typing import Optional

import httpx
from bs4 import BeautifulSoup

SOURCE = "editorial_rss"

RSS_FEEDS: list[tuple[str, str]] = [
    ("vogue_fashion",   "https://www.vogue.com/feed/fashion/rss"),
    ("vogue_shopping",  "https://www.vogue.com/feed/shopping/rss"),
    ("harpersbazaar",   "https://www.harpersbazaar.com/rss/fashion.xml"),
    ("wwd",             "https://wwd.com/feed/"),
    ("whowhatwear",     "https://www.whowhatwear.com/feed/"),
    ("refinery29",      "https://www.refinery29.com/en-us/fashion/feed.rss"),
    ("elle_fashion",    "https://www.elle.com/rss/fashion.xml/"),
]

# Keywords that suggest the article is about a specific trend (vs news/celebrity)
TREND_SIGNAL_KEYWORDS: list[str] = [
    "trend", "trending", "wear", "wearing", "style", "styled", "outfit",
    "aesthetic", "look", "looks", "season", "summer", "spring", "fall", "winter",
    "2026", "now", "moment", "rise", "rising", "comeback", "revival", "return",
    "obsess", "everywhere", "spotted", "street style", "runway", "collection",
    "micro", "macro", "core", "fashion week", "off duty", "it girl", "must-have",
    "best", "top", "new", "latest", "biggest", "hottest", "editor", "recommend",
]

# Keywords that indicate it's NOT a useful trend signal
NOISE_KEYWORDS: list[str] = [
    "obituary", "dies", "death", "passed away", "rip", "hiring",
    "coordinator", "job", "career", "executive", "appoints", "names ceo",
    "earnings", "revenue", "acquisition", "merger", "ipo",
    "review:", "recap:", "watch:", "listen:", "podcast",
    # Travel / listicles / lifestyle (not fashion trends)
    "airbnb", "hotel", "restaurant", "recipe", "travel", "vacation",
    "gift guide", "gift ideas", "father's day", "mother's day",
    "body oil", "skincare", "moisturizer", "peptide", "collagen",
    "bridesmaid robe", "bachelorette", "wedding guest dress",
    "best deals", "sale worth", "half-yearly sale", "memorial day deal",
    "celebrity look of the week", "celebrity airport", "cannes film festival",
    "red carpet", "film festival", "award show",
    # Generic round-ups that aren't about a specific trend
    "best activewear brands", "best tote bags", "best jeans for women",
    "best workout sets", "best loafers for women",
    "best sandals", "best bags", "best sunglasses",
    # Non-fashion subjects
    "susan boyle", "apple martin", "chase infiniti",
]

# Signals that strongly indicate a TREND (title must match at least one)
STRONG_TITLE_SIGNALS: list[str] = [
    "trend", "trending", "aesthetic", "comeback", "revival", "is back",
    "making a return", "having a moment", "everywhere", "taking off",
    "the new ", "rise of", "rising", "is the new", "going viral",
    "just became", "officially", "about to be", "micro trend",
    "season's", "2026's", "summer 2026", "spring 2026", "fall 2026",
    "you'll be wearing", "everyone is wearing",
]


def _is_trend_signal(title: str, description: str) -> bool:
    """Return True if the article is likely about a specific fashion trend."""
    title_lower = title.lower()
    text = (title + " " + description).lower()

    # Hard noise filter — reject immediately
    if any(kw in text for kw in NOISE_KEYWORDS):
        return False

    # Title must contain a strong trend signal word/phrase
    if not any(kw in title_lower for kw in STRONG_TITLE_SIGNALS):
        return False

    # Must also contain a fashion-domain keyword somewhere
    return any(kw in text for kw in TREND_SIGNAL_KEYWORDS)


def _clean_text(text: Optional[str]) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return " ".join(soup.get_text(separator=" ").split())


def _scrape_feed(label: str, url: str) -> list[dict]:
    """Fetch one RSS feed and return signal dicts."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }
    try:
        resp = httpx.get(url, headers=headers, timeout=20, follow_redirects=True)
        resp.raise_for_status()
    except Exception as e:
        print(f"[editorial_rss] {label} error: {e}")
        return []

    soup = BeautifulSoup(resp.text, "xml")
    items = soup.find_all("item")

    results = []
    for item in items:
        title_tag = item.find("title")
        desc_tag  = item.find("description") or item.find("summary")
        link_tag  = item.find("link")

        title = _clean_text(title_tag.text if title_tag else "")
        desc  = _clean_text(desc_tag.text if desc_tag else "")
        url_  = link_tag.text.strip() if link_tag else ""

        if not title or len(title) < 8:
            continue
        if not _is_trend_signal(title, desc):
            continue

        results.append({
            "title":       title,
            "description": desc[:400] if desc else title,
            "url":         url_,
            "source":      SOURCE,
            "feed":        label,
        })

    return results


def scrape() -> list[dict]:
    """Scrape all RSS feeds and return combined trend signal dicts."""
    all_results: list[dict] = []
    seen_titles: set[str] = set()

    for label, url in RSS_FEEDS:
        time.sleep(random.uniform(0.5, 1.5))
        signals = _scrape_feed(label, url)

        for s in signals:
            norm = s["title"].lower().strip()
            if norm not in seen_titles:
                seen_titles.add(norm)
                all_results.append(s)

    print(f"[editorial_rss] {len(all_results)} trend signals from {len(RSS_FEEDS)} feeds")
    return all_results


if __name__ == "__main__":
    import json
    data = scrape()
    for d in data:
        print(f"[{d['feed']}] {d['title'][:80]}")
