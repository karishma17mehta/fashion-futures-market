"""
Scraper for TrendHunter fashion trends slideshow page.
Returns list of dicts: {title, description, url, source}
"""
import random
import time
import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://www.trendhunter.com/slideshow/fashion-trends"
SOURCE = "trendhunter"

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]


def _random_headers() -> dict:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.google.com/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
    }


def _parse_trends(soup: BeautifulSoup) -> list[dict]:
    results = []
    seen: set[str] = set()

    # TrendHunter slideshow: each slide is typically an <article> or <li> with class containing "trend"
    candidates = soup.find_all(
        ["article", "li", "div"],
        class_=lambda c: c and any(
            token in c for token in ["trend", "slide", "item", "card", "story"]
        ),
    )

    for item in candidates:
        # Title
        heading = item.find(["h1", "h2", "h3", "h4", "h5"])
        if not heading:
            heading = item.find(class_=lambda c: c and "title" in c)
        title = heading.get_text(strip=True) if heading else ""

        if not title or len(title) < 4:
            continue

        # URL
        anchor = item.find("a", href=True)
        url = ""
        if anchor:
            href = anchor["href"]
            url = href if href.startswith("http") else "https://www.trendhunter.com" + href

        if url in seen and url:
            continue

        # Description
        desc_tag = item.find(
            ["p", "span", "div"],
            class_=lambda c: c and any(
                token in c for token in ["desc", "summary", "excerpt", "body", "text", "copy"]
            ),
        )
        if not desc_tag:
            # fall back to first <p>
            desc_tag = item.find("p")
        description = desc_tag.get_text(strip=True) if desc_tag else ""

        if url:
            seen.add(url)
        results.append({
            "title": title,
            "description": description,
            "url": url,
            "source": SOURCE,
        })

    return results


def scrape() -> list[dict]:
    """Scrape TrendHunter fashion slideshow and return signal dicts."""
    results = []
    try:
        time.sleep(random.uniform(2, 5))
        with httpx.Client(timeout=30, follow_redirects=True) as client:
            response = client.get(BASE_URL, headers=_random_headers())
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = _parse_trends(soup)

        # Fallback: grab all anchors with /trends/ in URL that have meaningful text
        if not results:
            seen: set[str] = set()
            for anchor in soup.find_all("a", href=True):
                href = anchor["href"]
                if "/trends/" not in href and "/trend/" not in href:
                    continue
                url = href if href.startswith("http") else "https://www.trendhunter.com" + href
                if url in seen:
                    continue
                title = anchor.get_text(strip=True)
                if len(title) < 5:
                    continue
                seen.add(url)
                results.append({
                    "title": title,
                    "description": "",
                    "url": url,
                    "source": SOURCE,
                })

    except Exception as exc:  # noqa: BLE001
        print(f"[trendhunter_scraper] Error: {exc}")
        return []

    print(f"[trendhunter_scraper] Found {len(results)} trends.")
    return results


if __name__ == "__main__":
    import json
    data = scrape()
    print(json.dumps(data[:5], indent=2))
