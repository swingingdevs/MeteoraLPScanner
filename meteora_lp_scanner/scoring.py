from datetime import datetime, timezone
from dateutil.parser import isoparse


def safe_float(value, default=0.0):
    try:
        if value is None:
            return default
        if isinstance(value, str):
            value = value.replace("%", "").strip()
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


def calc_vol_pct(current_price, last_price):
    if last_price <= 0:
        return 0.0
    return abs(current_price - last_price) / last_price * 100.0


def suggest_strategy(age_hours, vol_pct, bin_step):
    if age_hours <= 24 and vol_pct >= 5:
        return "Spot-Spread (20–30 bins)"
    if vol_pct >= 10:
        return "Spot-Wide (survival mode)"
    if age_hours <= 72:
        return "Bid-Ask (DCA style)"
    return "Spot-Spread (moderate)"


def suggest_hold(age_hours, vol_pct):
    if age_hours <= 24:
        return "2–8 hours (farm early chaos)"
    if vol_pct >= 10:
        return "1–6 hours (tight risk controls)"
    return "6–24 hours (monitor decay)"


def compute_score(apr, base_fee_pct, vol_pct, age_hours):
    freshness_boost = 20.0 if age_hours <= 24 else (10.0 if age_hours <= 72 else 0.0)
    score = (
        apr * 0.8
        + base_fee_pct * 10.0
        + min(vol_pct, 25.0) * 1.2
        + freshness_boost
    )
    return score
