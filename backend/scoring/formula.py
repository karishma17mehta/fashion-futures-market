"""
Fashion Futures Market — Trend Scoring Formula
===============================================
Computes a deterministic 0–10 score from real signal data.
No LLM numbers enter here. Claude is used only for narrative generation.

Score breakdown:
    velocity     0.30  — how fast is it growing right now?
    acceleration 0.20  — is that growth itself speeding up?
    novelty      0.25  — is this genuinely new or established?
    volume       0.10  — does it have real search mass?
    cross_platform 0.15 — does it appear on multiple independent sources?

Final score is multiplied by seasonality_multiplier (0.5–1.0) to
discount trends that are purely seasonal spikes.

Adding new data sources:
    1. Pass them into cross_platform_score() via platform_signals dict
    2. Adjust weights in WEIGHTS if needed
    3. The formula self-documents — every input is traceable to a source
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional

from scoring.features import (
    velocity_score,
    acceleration_score,
    novelty_score,
    volume_score,
    cross_platform_score,
    seasonality_multiplier,
)

# Component weights — must sum to 1.0
WEIGHTS = {
    "velocity":       0.30,
    "acceleration":   0.20,
    "novelty":        0.25,
    "volume":         0.10,
    "cross_platform": 0.15,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, "Weights must sum to 1.0"


class TrendSignalData:
    """
    Container for all raw signal inputs to the scoring formula.
    Pass what you have — None values fall back to neutral scores.

    Required for meaningful scoring (at minimum):
        - monthly_change_pct    (from Pinterest or Google Trends)
        - yoy_change_pct        (from Pinterest)
        - weekly_volumes        (13-week series from Pinterest)

    Improves scoring significantly:
        - weekly_change_pct
        - normalized_volume
        - platform_signals (especially non-search platforms)

    Future data hooks (set to None until you have data):
        - tiktok_growth_pct
        - depop_search_rank
        - instagram_hashtag_count
        - lyst_appearance
    """
    def __init__(
        self,
        trend_name: str,

        # Pinterest / Google Trends data
        monthly_change_pct:  Optional[float] = None,
        weekly_change_pct:   Optional[float] = None,
        yoy_change_pct:      Optional[float] = None,
        normalized_volume:   Optional[float] = None,
        weekly_volumes:      Optional[list[int]] = None,  # 8-13 weeks

        # Platform presence flags / metrics
        on_pinterest:        bool | float = False,
        on_google_trends:    bool | float = False,
        on_reddit:           bool | float = False,

        # Real signal data — now wired in from TikTok, Depop, Google Shopping
        tiktok_growth_pct:    Optional[float] = None,  # TikTok WoW % (e.g. 1647.0)
        depop_search_rank:    Optional[int]   = None,  # 1=annual report, 2=monthly, 3=mentioned
        google_shopping_pct:  Optional[float] = None,  # Google Shopping RISING %
        instagram_count:      Optional[int]   = None,  # Instagram hashtag post count
        lyst_appearance:      bool = False,             # In Lyst Index
    ):
        self.trend_name          = trend_name
        self.monthly_change_pct  = monthly_change_pct
        self.weekly_change_pct   = weekly_change_pct
        self.yoy_change_pct      = yoy_change_pct
        self.normalized_volume   = normalized_volume
        self.weekly_volumes      = weekly_volumes or []

        # Build platform signals dict
        self.platform_signals: dict[str, bool | float] = {
            "pinterest":  on_pinterest,
            "google":     on_google_trends,
            "reddit":     on_reddit,
        }

        # TikTok: store actual WoW growth % so cross_platform_score
        # can weight high-velocity TikTok signals more than low-velocity ones.
        # 1,647% WoW on TikTok ≠ 30% WoW — this distinction matters.
        # Floor at 1.0 (minimum presence signal) so confirmed-TikTok hashtags
        # with 0% WoW (e.g. same-day re-scrape, or stable established trends)
        # still register platform presence rather than being silently dropped.
        if tiktok_growth_pct is not None:
            self.platform_signals["tiktok"] = max(1.0, tiktok_growth_pct)

        # Depop: confidence level based on how prominently featured.
        # Annual report top-4 = purchase-intent with high editorial conviction (1.0).
        # Monthly trending = real signal, less curated (0.7).
        # Mentioned = weak confirmation (0.5).
        if depop_search_rank is not None:
            confidence = {1: 1.0, 2: 0.7, 3: 0.5}.get(depop_search_rank, 0.5)
            self.platform_signals["depop"] = confidence

        # Google Shopping: purchase-intent search data, separate weight from
        # informational Google Trends. Store RISING % for log-scaled weighting.
        if google_shopping_pct is not None and google_shopping_pct > 0:
            self.platform_signals["google_shopping"] = google_shopping_pct

        if instagram_count is not None:
            self.platform_signals["instagram"] = instagram_count > 10_000
        if lyst_appearance:
            self.platform_signals["lyst"] = True


class ScoreResult:
    def __init__(
        self,
        final_score: float,
        components: dict[str, float],
        seasonality_mult: float,
        data_completeness: float,
    ):
        self.score              = final_score
        self.components         = components  # each component's raw 0-10 value
        self.seasonality_mult   = seasonality_mult
        self.data_completeness  = data_completeness  # 0-1, how much data we had

    def __repr__(self) -> str:
        comps = ", ".join(f"{k}={v:.1f}" for k, v in self.components.items())
        return (
            f"ScoreResult(score={self.score:.1f}, "
            f"seasonal_mult={self.seasonality_mult:.2f}, "
            f"completeness={self.data_completeness:.0%}, "
            f"[{comps}])"
        )


def compute_score(data: TrendSignalData, month: Optional[int] = None) -> ScoreResult:
    """
    Main scoring entry point.

    Args:
        data:  TrendSignalData with all available signals
        month: current month (1-12) for seasonality check.
               Defaults to today's month.

    Returns:
        ScoreResult with final score, component breakdown, and metadata.
    """
    if month is None:
        month = datetime.now().month

    # ── Compute each component ────────────────────────────────────────────────
    v_score  = velocity_score(data.monthly_change_pct, data.weekly_change_pct, data.yoy_change_pct)
    a_score  = acceleration_score(data.weekly_volumes)
    n_score  = novelty_score(data.yoy_change_pct, data.monthly_change_pct, data.normalized_volume)
    vol_score = volume_score(data.normalized_volume)
    cp_score = cross_platform_score(data.platform_signals)

    components = {
        "velocity":       v_score,
        "acceleration":   a_score,
        "novelty":        n_score,
        "volume":         vol_score,
        "cross_platform": cp_score,
    }

    # ── Weighted sum ──────────────────────────────────────────────────────────
    raw = sum(WEIGHTS[k] * components[k] for k in WEIGHTS)

    # ── Seasonality adjustment ────────────────────────────────────────────────
    s_mult = seasonality_multiplier(data.trend_name, month)
    final  = round(min(10.0, max(0.0, raw * s_mult)), 1)

    # ── Data completeness (transparency metric) ───────────────────────────────
    available = sum([
        data.monthly_change_pct is not None,
        data.yoy_change_pct     is not None,
        data.normalized_volume  is not None,
        len(data.weekly_volumes) >= 8,
        any(data.platform_signals.values()),
    ])
    completeness = available / 5.0

    return ScoreResult(
        final_score        = final,
        components         = components,
        seasonality_mult   = s_mult,
        data_completeness  = completeness,
    )


def score_from_pinterest_row(
    trend_name: str,
    normalized_volume: float,
    weekly_change_pct: float,
    monthly_change_pct: float,
    yoy_change_pct: float,
    weekly_volumes: list[int],
    also_on_google: bool = False,
    also_on_reddit: bool = False,
) -> ScoreResult:
    """
    Convenience wrapper for scoring directly from a Pinterest CSV row.
    This is the primary scoring path for auto-scraped trends.
    """
    data = TrendSignalData(
        trend_name         = trend_name,
        normalized_volume  = normalized_volume,
        weekly_change_pct  = weekly_change_pct,
        monthly_change_pct = monthly_change_pct,
        yoy_change_pct     = yoy_change_pct,
        weekly_volumes     = weekly_volumes,
        on_pinterest       = normalized_volume,   # volume as signal strength
        on_google_trends   = also_on_google,
        on_reddit          = also_on_reddit,
    )
    return compute_score(data)


def score_from_google_trends(
    trend_name: str,
    weekly_volumes: list[int],
    velocity_pct: float,
    also_on_reddit: bool = False,
) -> ScoreResult:
    """
    Convenience wrapper for scoring from Google Trends data.
    Uses velocity as monthly_change proxy.
    """
    data = TrendSignalData(
        trend_name          = trend_name,
        monthly_change_pct  = velocity_pct,
        weekly_volumes      = weekly_volumes,
        normalized_volume   = max(weekly_volumes) if weekly_volumes else None,
        on_google_trends    = True,
        on_reddit           = also_on_reddit,
    )
    return compute_score(data)
