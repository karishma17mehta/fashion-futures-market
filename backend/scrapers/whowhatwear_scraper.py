"""
Scraper for WhoWhatWear UK fashion trends page.
Returns list of dicts: {title, url, source, keywords}
"""
import random
import time
import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://www.whowhatwear.com/uk/fashion/trends"
SOURCE = "whowhatwear"

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]

TREND_KEYWORDS = [
    "sheer", "layering", "quiet luxury", "balletcore", "gorpcore",
    "mob wife", "coastal grandmother", "dark academia", "coquette",
    "indie sleaze", "old money", "cottagecore", "Y2K", "dopamine",
    "maximalism", "barbiecore", "minimalism", "boho", "preppy",
    "streetwear", "athleisure", "grunge", "punk", "romantic",
    "western", "utility", "vintage", "retro", "aesthetic",
]


def _random_headers() -> dict:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
    }


def _extract_keywords(text: str) -> list[str]:
    text_lower = text.lower()
    return [kw for kw in TREND_KEYWORDS if kw in text_lower]


def scrape() -> list[dict]:
    """Scrape WhoWhatWear trends page and return article signal dicts."""
    results = []
    try:
        time.sleep(random.uniform(2, 5))
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(BASE_URL, headers=_random_headers())
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Primary: structured article cards
        article_cards = soup.find_all(
            ["article", "div"],
            class_=lambda c: c and any(
                token in c for token in ["article", "card", "post", "item", "story", "tile"]
            ),
        )

        seen_urls: set[str] = set()

        for card in article_cards:
            anchor = card.find("a", href=True)
            if not anchor:
                continue
            url = anchor["href"]
            if not url.startswith("http"):
                url = "https://www.whowhatwear.com" + url
            if url in seen_urls:
                continue

            # Try to find a heading inside the card
            heading = card.find(["h1", "h2", "h3", "h4"])
            title = heading.get_text(strip=True) if heading else anchor.get_text(strip=True)
            if not title:
                continue

            keywords = _extract_keywords(title)
            # Also check any visible body text inside card
            body_text = card.get_text(" ", strip=True)
            for kw in _extract_keywords(body_text):
                if kw not in keywords:
                    keywords.append(kw)

            seen_urls.add(url)
            results.append({
                "title": title,
                "url": url,
                "source": SOURCE,
                "keywords": keywords,
            })

        # Fallback: all anchors that look like article links
        if not results:
            for anchor in soup.find_all("a", href=True):
                url = anchor["href"]
                if not url.startswith("http"):
                    url = "https://www.whowhatwear.com" + url
                if "/fashion/" not in url and "/style/" not in url:
                    continue
                if url in seen_urls:
                    continue
                title = anchor.get_text(strip=True)
                if len(title) < 10:
                    continue
                keywords = _extract_keywords(title)
                seen_urls.add(url)
                results.append({
                    "title": title,
                    "url": url,
                    "source": SOURCE,
                    "keywords": keywords,
                })

    except Exception as exc:  # noqa: BLE001
        print(f"[whowhatwear_scraper] Error: {exc}")
        return []

    print(f"[whowhatwear_scraper] Found {len(results)} articles.")
    return results


if __name__ == "__main__":
    import json
    data = scrape()
    print(json.dumps(data[:5], indent=2))
