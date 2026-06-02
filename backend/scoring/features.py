"""
Feature extraction for trend scoring.
Each function returns a float 0.0–10.0.

Calibration targets (what scores should look like with real Pinterest data):
    +10,000% YoY, +200% monthly, vol 100  → velocity ~8.5, novelty ~8.0
    +600%    YoY, +40%  monthly, vol 60   → velocity ~7.0, novelty ~7.5
    +200%    YoY, +10%  monthly, vol 40   → velocity ~5.5, novelty ~6.5
    +20%     YoY, +5%   monthly, vol 90   → velocity ~4.0, novelty ~3.0
    Established term (high vol, low growth) → velocity ~3.0, novelty ~2.0
"""
from __future__ import annotations
import math
from typing import Optional


# ── Velocity ─────────────────────────────────────────────────────────────────

def _pct_to_velocity(pct: float) -> float:
    """
    Piecewise linear map from % growth to 0-10 velocity score.
    Calibrated so that:
        +10,000%+ → 9.5
        +1,000%   → 8.0
        +200%     → 6.5
        +100%     → 5.5
        +30%      → 4.5
        +10%      → 4.0
        0%        → 3.0
        -30%      → 1.5
        -100%     → 0.0
    """
    if pct >= 1000:
        return min(9.5, 8.0 + (pct - 1000) / 9000)
    if pct >= 100:
        return 5.5 + (pct - 100) / 900 * 2.5
    if pct >= 10:
        return 4.0 + (pct - 10) / 90 * 1.5
    if pct >= 0:
        return 3.0 + pct / 10
    # Negative growth
    return max(0.0, 3.0 + pct / 43)


def velocity_score(
    monthly_change_pct: Optional[float],
    weekly_change_pct:  Optional[float] = None,
    yoy_change_pct:     Optional[float] = None,
) -> float:
    """
    How fast is the trend growing right now?

    Three signals, each at a different time horizon:
      - Monthly (primary): near-term momentum
      - Weekly (recency blend): very recent acceleration
      - YoY (horizon signal): if YoY is dramatically higher than monthly,
        the trend has sustained structural breakout — use the max so explosive
        multi-year growth doesn't get suppressed by a quieter single month.

    Blending:
      1. Start with monthly (or 5.0 if missing)
      2. Blend in weekly at 25%
      3. If YoY score > blended score, take max (YoY discounted 10% for
         being a longer timeframe than month-level signal)
    """
    if monthly_change_pct is None and yoy_change_pct is None:
        return 5.0

    # Monthly base
    if monthly_change_pct is not None:
        base = _pct_to_velocity(monthly_change_pct)
    else:
        base = 5.0

    # Blend in weekly recency
    if weekly_change_pct is not None:
        weekly = _pct_to_velocity(weekly_change_pct)
        base = 0.75 * base + 0.25 * weekly

    # YoY horizon signal — discount 10% vs near-term but use if stronger
    if yoy_change_pct is not None:
        yoy_score = _pct_to_velocity(yoy_change_pct) * 0.90
        base = max(base, yoy_score)

    return round(base, 2)


# ── Acceleration ──────────────────────────────────────────────────────────────

def acceleration_score(weekly_volumes: list[int]) -> float:
    """
    Is growth speeding up or flattening?
    Compares slope of last 4 weeks vs slope of prior 4 weeks.
    Requires at least 8 weekly data points (Pinterest gives 13).
    """
    if len(weekly_volumes) < 8:
        return 5.0

    recent = weekly_volumes[-4:]
    prior  = weekly_volumes[-8:-4]

    def slope(series: list[int]) -> float:
        n = len(series)
        if n < 2:
            return 0.0
        x_mean = (n - 1) / 2
        y_mean = sum(series) / n
        num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(series))
        den = sum((i - x_mean) ** 2 for i in range(n))
        return num / den if den != 0 else 0.0

    s_recent = slope(recent)
    s_prior  = slope(prior)

    if s_prior == 0:
        ratio = 2.0 if s_recent > 0 else 0.5
    else:
        ratio = s_recent / abs(s_prior)

    score = 5.0 + min(5.0, max(-5.0, ratio * 2.5))
    return round(score, 2)


# ── Novelty ───────────────────────────────────────────────────────────────────

def novelty_score(
    yoy_change_pct:     Optional[float],
    monthly_change_pct: Optional[float] = None,
    normalized_volume:  Optional[float] = None,
) -> float:
    """
    Is this genuinely new or an established term?

    Three cases:
    1. High YoY + moderate volume  → truly emerging (high novelty)
    2. Negative YoY + high monthly → re-emerging after a dormant period
    3. Low YoY + high volume       → established, mainstream (low novelty)

    Volume penalty: very high volume terms lose novelty points because
    they're already mainstream (e.g. 'nails' at 100 is not underground).
    """
    # Case 1 & 3: use YoY as primary signal
    if yoy_change_pct is not None and yoy_change_pct >= 0:
        base = _pct_to_velocity(yoy_change_pct)

    # Case 2: re-emerging trend (negative YoY but strong recent growth)
    elif yoy_change_pct is not None and yoy_change_pct < 0:
        if monthly_change_pct is not None and monthly_change_pct > 50:
            # Re-emergence: give credit for current momentum, discount for prior decline
            re_emerge = _pct_to_velocity(monthly_change_pct) * 0.7
            base = max(1.5, re_emerge)
        else:
            base = max(0.0, 3.0 + yoy_change_pct / 50)

    else:
        return 5.0  # no data

    # Volume penalty: terms already at very high volume are less underground
    if normalized_volume is not None and normalized_volume > 50:
        penalty = ((normalized_volume - 50) / 50) * 2.5
        base = max(0.0, base - penalty)

    return round(base, 2)


# ── Volume ────────────────────────────────────────────────────────────────────

def volume_score(normalized_volume: Optional[float]) -> float:
    """
    Absolute search mass. Weighted low (0.10) in the final formula.
    Pinterest normalized volume: 0-100 (100 = platform peak).
    """
    if normalized_volume is None:
        return 5.0
    return round(normalized_volume / 10, 2)


# ── Cross-platform ────────────────────────────────────────────────────────────

# Base weights per platform — reflects signal quality, not just reach.
# Search platforms (Pinterest, Google): inspiration/discovery intent.
# Purchase platforms (Depop, Lyst): transactional intent — highest weight.
# Social platforms (TikTok, Reddit): cultural validation — high weight.
# Google Shopping: purchase-intent search, above regular Google.
_PLATFORM_WEIGHTS: dict[str, float] = {
    "pinterest":       2.0,   # visual search / inspiration
    "google":          2.0,   # informational search
    "google_shopping": 2.5,   # purchase-intent search
    "reddit":          3.0,   # community validation
    "tiktok":          3.0,   # viral / cultural signal
    "depop":           3.5,   # resale purchase intent
    "instagram":       2.5,   # social discovery
    "lyst":            3.5,   # actual shopping behaviour
}


def _platform_strength(value: bool | float) -> float:
    """
    Convert a platform signal value to a 0–1 strength multiplier.

    Value semantics (set in TrendSignalData):
      - True / False   → confirmed present (1.0) or absent (0.0)
      - float 0–1      → confidence score (e.g. Depop: 1.0=annual report,
                          0.7=monthly trending, 0.5=mentioned)
      - float > 1      → growth % (TikTok WoW, Google Shopping RISING %)
                          Scaled logarithmically so 1,647% >> 30% but
                          both are still meaningful signals.
                          30% → ~0.45   100% → ~0.55   500% → ~0.75
                          1,000% → ~0.85   2,000%+ → 1.0
    """
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if value <= 0:
        return 0.0
    if value <= 1.0:
        return float(value)                        # confidence score
    # Growth % — log scale capped at 1.0
    return min(1.0, 0.35 + 0.65 * (math.log10(value) / math.log10(3000)))


def cross_platform_score(platform_signals: dict[str, bool | float]) -> float:
    """
    Multi-source confirmation score (0–10).

    Each platform contributes: base_weight × signal_strength
    Signal strength encoding:
      - boolean True          → 1.0 (confirmed)
      - float 0–1             → confidence (e.g. 0.7 = monthly Depop trending)
      - float > 1             → growth % (TikTok WoW, Google Shopping RISING)
                                 scaled logarithmically

    Convergence bonus — when independent sources agree, confidence compounds:
      3+ sources → ×1.15    4+ sources → additional ×1.10
    This rewards trends that show up on TikTok AND Depop AND Pinterest
    far more than a trend only visible on one high-weight platform.
    """
    total = 0.0
    n_active = 0

    for platform, value in platform_signals.items():
        strength = _platform_strength(value)
        if strength <= 0:
            continue
        base = _PLATFORM_WEIGHTS.get(platform, 2.0)
        total += base * strength
        n_active += 1

    # Convergence bonus: independent corroboration reduces false-positive risk
    if n_active >= 3:
        total *= 1.15
    if n_active >= 4:
        total *= 1.10

    return round(min(10.0, total), 2)


# ── Seasonality ───────────────────────────────────────────────────────────────

SEASONAL_PATTERNS: list[tuple[str, list[int]]] = [
    # ── Holidays / events ──────────────────────────────────────────────────────
    ("graduation",      [4, 5, 6]),
    ("mothers day",     [4, 5]),
    ("memorial day",    [5]),
    ("fourth of july",  [6, 7]),
    ("4th of july",     [6, 7]),
    ("patriotic",       [6, 7]),
    ("halloween",       [9, 10]),
    ("christmas",       [11, 12]),
    ("valentines",      [1, 2]),
    ("prom",            [3, 4, 5]),
    ("back to school",  [7, 8]),
    ("homecoming",      [7, 8, 9, 10]),
    ("bridal",          [3, 4, 5, 6]),
    ("sequin",          [11, 12]),
    ("party dress",     [11, 12]),
    # ── Seasonal nails ─────────────────────────────────────────────────────────
    ("june nails",      [5, 6]),
    ("may nails",       [4, 5]),
    ("july nails",      [6, 7]),
    ("fall nails",      [8, 9, 10]),
    ("winter nails",    [11, 12, 1]),
    ("spring nails",    [2, 3, 4]),
    # Summer nails is NOT in here — it's a year-specific query, structural not seasonal
    # ── Seasonal clothing ──────────────────────────────────────────────────────
    ("mini skirt",      [5, 6, 7]),
    ("tennis skirt",    [5, 6, 7]),
    ("jorts",           [4, 5, 6, 7]),
    ("denim shorts",    [4, 5, 6, 7]),
    ("gingham",         [4, 5, 6]),
    ("western boot",    [4, 5, 6, 7]),
    ("corset top",      [9, 10, 11]),
    ("linen pant",      [3, 4, 5, 6]),
    ("linen trouser",   [3, 4, 5, 6]),
    ("linen set",       [3, 4, 5, 6]),
]

def seasonality_multiplier(trend_name: str, current_month: int) -> float:
    """
    Penalty for trends that are purely seasonal spikes.
    We don't zero them out — a trend peaking now is still tradeable.
    We just discount it so it doesn't outscore structural trends.

    1.00 = no seasonal pattern → full score
    0.82 = in peak seasonal window (e.g. graduation nails in May)
    0.92 = seasonal pattern but currently off-peak
    """
    name_lower = trend_name.lower()
    for keyword, peak_months in SEASONAL_PATTERNS:
        if keyword in name_lower:
            if current_month in peak_months:
                return 0.82   # in peak — real spike but will fade
            else:
                return 0.92   # seasonal pattern, currently off-peak
    return 1.0
