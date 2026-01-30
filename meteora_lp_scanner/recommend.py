from dataclasses import dataclass
from typing import List, Dict

from .api import fetch_all_pairs
from .scoring import (
    safe_float,
    calc_age_hours,
    calc_move_pct,
    compute_score,
    suggest_strategy,
    suggest_hold,
)
from .storage import load_first_seen, save_first_seen, load_snapshots, save_snapshots, now_iso


@dataclass
class ScannerConfig:
    days: float = 3.0
    top: int = 15
    min_tvl: float = 0.0
    min_vol24h: float = 0.0
    min_fees24h: float = 0.0
    new_only: bool = False


def _pair_name(pair: Dict) -> str:
    name = pair.get("name")
    if name:
        return name
    symbol_x = pair.get("token_x_symbol") or pair.get("symbol_x")
    symbol_y = pair.get("token_y_symbol") or pair.get("symbol_y")
    if symbol_x and symbol_y:
        return f"{symbol_x}/{symbol_y}"
    return pair.get("address") or pair.get("pair_address") or "UNKNOWN"


def _get_metric(pair: Dict, *keys: str) -> float:
    for key in keys:
        if key in pair and pair.get(key) is not None:
            return safe_float(pair.get(key), 0.0)
    return 0.0


def get_recommendations(config: ScannerConfig) -> List[Dict]:
    first_seen = load_first_seen()
    snapshots = load_snapshots()
    now = now_iso()

    pairs = fetch_all_pairs()
    recommendations: List[Dict] = []

    for pair in pairs:
        pair_addr = pair.get("pair_address") or pair.get("address") or ""
        if not pair_addr:
            continue

        is_new = False
        if pair_addr not in first_seen:
            first_seen[pair_addr] = now
            is_new = True

        age_hours = calc_age_hours(first_seen[pair_addr])
        if age_hours > config.days * 24:
            continue
        if config.new_only and not is_new:
            continue

        tvl = _get_metric(pair, "tvl", "liquidity", "tvl_usd")
        vol_24h = _get_metric(pair, "volume_24h", "trade_volume_24h", "volume_24h_usd")
        fees_24h = _get_metric(pair, "fees_24h", "fee_24h", "fees")
        current_price = _get_metric(pair, "current_price", "price")

        if tvl < config.min_tvl or vol_24h < config.min_vol24h or fees_24h < config.min_fees24h:
            continue

        history = snapshots.get(pair_addr, [])
        last_snapshot = history[-1] if history else {}
        last_price = safe_float(last_snapshot.get("current_price"), 0.0)
        move_pct = calc_move_pct(current_price, last_price)

        vol_per_min = vol_24h / (24 * 60) if vol_24h else 0.0
        fees_per_min = fees_24h / (24 * 60) if fees_24h else 0.0

        score = compute_score(tvl, vol_24h, fees_24h, move_pct, age_hours)
        strategy = suggest_strategy(age_hours, move_pct, vol_per_min, fees_per_min)
        hold = suggest_hold(age_hours, move_pct)

        recommendations.append(
            {
                "name": _pair_name(pair),
                "tvl": tvl,
                "volume_24h": vol_24h,
                "fees_24h": fees_24h,
                "vol_per_min": vol_per_min,
                "fees_per_min": fees_per_min,
                "move_pct": move_pct,
                "age_hours": age_hours,
                "score": score,
                "strategy": strategy,
                "hold": hold,
                "pair_address": pair_addr,
            }
        )

        history.append(
            {
                "timestamp": now,
                "current_price": current_price,
                "volume_24h": vol_24h,
                "fees_24h": fees_24h,
                "tvl": tvl,
            }
        )
        snapshots[pair_addr] = history[-50:]

    recommendations.sort(key=lambda item: item["score"], reverse=True)
    recommendations = recommendations[: config.top]

    save_first_seen(first_seen)
    save_snapshots(snapshots)

    return recommendations
