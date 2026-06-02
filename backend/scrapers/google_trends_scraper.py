"""
Google Trends scraper using pytrends.
Queries rising fashion search terms and returns velocity scores (% change over 90 days).
Returns list of dicts: {term, velocity_score, rising_queries, source}
"""
import time
import random
from pytrends.request import TrendReq

SOURCE = "google_trends"

SEED_AESTHETICS = [
    "sheer layering",
    "quiet luxury",
    "balletcore",
    "gorpcore",
    "mob wife aesthetic",
    "coastal grandmother",
    "dark academia",
    "coquette aesthetic",
    "indie sleaze",
    "old money style",
    "cottagecore",
    "Y2K fashion",
    "dopamine dressing",
    "maximalism fashion",
    "barbiecore",
]

# pytrends processes max 5 keywords per request
_BATCH_SIZE = 5


def _build_pytrends() -> TrendReq:
    return TrendReq(
        hl="en-US",
        tz=0,
        timeout=(10, 30),
        requests_args={
            "headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            }
        },
    )


def _batches(lst: list, size: int):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


def _velocity_from_interest(interest_df) -> float:
    """
    Compute velocity as % change from the first quarter of the period to the last quarter.
    Returns 0.0 if data is insufficient.
    """
    if interest_df is None or interest_df.empty:
        return 0.0
    try:
        # Use a single column if multi-keyword (take first non-isPartial column)
        cols = [c for c in interest_df.columns if c != "isPartial"]
        if not cols:
            return 0.0
        col = cols[0]
        series = interest_df[col].dropna()
        n = len(series)
        if n < 4:
            return 0.0
        quarter = max(1, n // 4)
        start_mean = series.iloc[:quarter].mean()
        end_mean = series.iloc[-quarter:].mean()
        if start_mean == 0:
            return 100.0 if end_mean > 0 else 0.0
        return round(((end_mean - start_mean) / start_mean) * 100, 2)
    except Exception:
        return 0.0


def scrape() -> list[dict]:
    """Query Google Trends for seed aesthetics and return velocity signal dicts."""
    results: list[dict] = []
    pytrends = _build_pytrends()

    for batch in _batches(SEED_AESTHETICS, _BATCH_SIZE):
        for term in batch:
            try:
                time.sleep(random.uniform(2, 5))
                pytrends.build_payload(
                    [term],
                    cat=185,          # Fashion & Style category
                    timeframe="today 3-m",
                    geo="",
                    gprop="",
                )

                # Interest over time (90 days)
                interest_df = pytrends.interest_over_time()
                velocity = _velocity_from_interest(interest_df)

                # Rising related queries
                related = pytrends.related_queries()
                rising_queries: list[str] = []
                if related and term in related:
                    rising_df = related[term].get("rising")
                    if rising_df is not None and not rising_df.empty:
                        rising_queries = rising_df["query"].tolist()[:10]

                results.append({
                    "term": term,
                    "velocity_score": velocity,
                    "rising_queries": rising_queries,
                    "source": SOURCE,
                })
                print(f"[google_trends_scraper] '{term}' velocity={velocity}%")

            except Exception as exc:  # noqa: BLE001
                print(f"[google_trends_scraper] Error for '{term}': {exc}")
                results.append({
                    "term": term,
                    "velocity_score": 0.0,
                    "rising_queries": [],
                    "source": SOURCE,
                })

    print(f"[google_trends_scraper] Processed {len(results)} terms.")
    return results


if __name__ == "__main__":
    import json
    data = scrape()
    print(json.dumps(data, indent=2))


def scrape_terms(terms: list[str]) -> list[dict]:
    """
    Query Google Trends for a custom list of terms (not just the seed list).
    Used by auto_resolve agent to check specific trend names.
    Same return format as scrape().
    """
    original = SEED_AESTHETICS[:]
    # Temporarily replace seed list
    import scrapers.google_trends_scraper as _self
    _self.SEED_AESTHETICS[:] = terms
    # Re-run using the existing batched logic but with provided terms
    results: list[dict] = []
    pytrends = _build_pytrends()
    for batch in _batches(terms, _BATCH_SIZE):
        for term in batch:
            try:
                time.sleep(random.uniform(1, 3))
                pytrends.build_payload([term], cat=185, timeframe="today 3-m", geo="", gprop="")
                interest_df = pytrends.interest_over_time()
                velocity = _velocity_from_interest(interest_df)
                weekly_vols = []
                if interest_df is not None and not interest_df.empty and term in interest_df.columns:
                    weekly_vols = interest_df[term].tolist()[-13:]
                results.append({
                    "term": term,
                    "velocity_score": velocity,
                    "weekly_volumes": weekly_vols,
                    "rising_queries": [],
                    "source": SOURCE,
                })
            except Exception as exc:
                results.append({
                    "term": term,
                    "velocity_score": 0.0,
                    "weekly_volumes": [],
                    "rising_queries": [],
                    "source": SOURCE,
                })
    return results
