import httpx
from bs4 import BeautifulSoup
from collections import Counter
import re
import time

# Depop doesn't have a public API — we scrape search results
# Rate limit aggressively to avoid blocks

DEPOP_BASE = "https://www.depop.com"
SEARCH_TERMS = [
    "y2k", "dark academia", "balletcore", "quiet luxury", "gorpcore",
    "coastal grandmother", "cottagecore", "old money", "mob wife",
    "coquette", "indie sleaze", "barbiecore"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def search_depop(term: str, limit: int = 50) -> list[dict]:
    """Scrape Depop search results for a given aesthetic term."""
    url = f"{DEPOP_BASE}/search/?q={term.replace(' ', '+')}"
    listings = []

    try:
        with httpx.Client(headers=HEADERS, timeout=10) as client:
            resp = client.get(url)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            # Depop renders client-side — parse what's available in initial HTML
            # Full implementation would use Playwright for JS-rendered content
            items = soup.find_all("article", limit=limit)
            for item in items:
                title = item.get("aria-label", "")
                if title:
                    listings.append({
                        "term": term,
                        "title": title,
                        "source": "depop",
                    })
    except Exception:
        pass

    time.sleep(2)  # be polite
    return listings


def measure_velocity(term: str) -> dict:
    """
    Compare listing count for a term now vs. baseline.
    In production: store historical counts in DB and compare.
    """
    current = search_depop(term)
    return {
        "term": term,
        "listing_count": len(current),
        "source": "depop",
        "listings_sample": current[:5],
    }


def run_depop_scrape() -> list[dict]:
    results = []
    for term in SEARCH_TERMS:
        result = measure_velocity(term)
        results.append(result)
    return results
