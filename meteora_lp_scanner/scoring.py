import math
from datetime import datetime, timezone

from dateutil.parser import isoparse


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        if isinstance(value, str):
            value = value.replace(",", "").replace("%", "").strip()
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def calc_age_hours(first_seen_iso):
    try:
        timestamp = isoparse(first_seen_iso)
        now = datetime.now(timezone.utc)
        return max(0.0, (now - timestamp).total_seconds() / 3600.0)
    except Exception:
        return 10**9


def calc_move_pct(current_price, last_price):
    if last_price <= 0:
        return 0.0
    return abs(current_price - last_price) / last_price * 100.0


def score_value(value, weight):
    return math.log10(1 + max(value, 0.0)) * weight


def compute_score(tvl, vol_24h, fees_24h, move_pct, age_hours):
    freshness = 12.0 if age_hours <= 24 else (6.0 if age_hours <= 72 else 0.0)
    score = (
        score_value(tvl, 4.0)
        + score_value(vol_24h, 6.0)
        + score_value(fees_24h, 10.0)
        + min(move_pct, 20.0) * 0.6
        + freshness
    )
    return score


def suggest_strategy(age_hours, move_pct, vol_per_min, fees_per_min):
    if age_hours <= 12 and move_pct >= 5:
        return "Spot-Spread (tight, high motion)"
    if fees_per_min >= 2:
        return "Fee-Farm (wider, harvest fees)"
    if vol_per_min >= 50:
        return "Momentum (adaptive ranges)"
    if age_hours <= 72:
        return "Discovery (moderate bins)"
    return "Conservative (wide, monitor)"


def suggest_hold(age_hours, move_pct):
    if age_hours <= 12:
        return "2–6 hours (early volatility)"
    if move_pct >= 10:
        return "1–4 hours (tight risk)"
    if age_hours <= 72:
        return "6–24 hours (recheck daily)"
    return "12–48 hours (monitor weekly)"
