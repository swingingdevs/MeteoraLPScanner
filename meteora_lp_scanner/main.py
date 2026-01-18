import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from meteora_api import fetch_all_pairs
from scoring import (
    safe_float,
    safe_int,
    calc_age_hours,
    calc_vol_pct,
    suggest_strategy,
    suggest_hold,
    compute_score,
)
from storage import (
    load_first_seen,
    save_first_seen,
    load_last_snapshot,
    save_last_snapshot,
    now_iso,
)


def main():
    parser = argparse.ArgumentParser(description="Meteora DLMM LP Ideas Scanner")
    parser.add_argument("--days", type=float, default=3.0)
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--min-apr", type=float, default=0.0)
    parser.add_argument("--new-only", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    args = parser.parse_args()

    console = Console()

    first_seen = load_first_seen()
    last_snapshot = load_last_snapshot()

    pairs = fetch_all_pairs()
    now = now_iso()

    recs = []
    for pair in pairs:
        pair_addr = pair.get("address") or pair.get("pair_address") or ""
        name = pair.get("name") or "UNKNOWN"
        if not pair_addr:
            continue

        if pair_addr not in first_seen:
            first_seen[pair_addr] = now

        age_hours = calc_age_hours(first_seen[pair_addr])
        if age_hours > args.days * 24:
            continue

        apr = safe_float(pair.get("apr"), 0.0)
        apy = safe_float(pair.get("apy"), 0.0)
        base_fee_pct = safe_float(pair.get("base_fee_percentage"), 0.0)
        bin_step = safe_int(pair.get("bin_step"), 0)
        current_price = safe_float(pair.get("current_price"), 0.0)

        mint_x = pair.get("mint_x") or pair.get("token_x_mint") or ""
        mint_y = pair.get("mint_y") or pair.get("token_y_mint") or ""

        last = last_snapshot.get(pair_addr, {})
        last_price = safe_float(last.get("current_price"), 0.0)
        vol_pct = calc_vol_pct(current_price, last_price)

        if apr < args.min_apr:
            continue

        is_new = last_snapshot.get(pair_addr) is None
        if args.new_only and not is_new:
            continue

        score = compute_score(apr, base_fee_pct, vol_pct, age_hours)
        strat = suggest_strategy(age_hours, vol_pct, bin_step)
        hold = suggest_hold(age_hours, vol_pct)

        recs.append(
            {
                "name": name,
                "pair_address": pair_addr,
                "mint_x": mint_x,
                "mint_y": mint_y,
                "apr_24h": apr,
                "apy_24h": apy,
                "base_fee_pct": base_fee_pct,
                "bin_step": bin_step,
                "current_price": current_price,
                "vol_pct": vol_pct,
                "age_hours": age_hours,
                "score": score,
                "strategy": strat,
                "hold": hold,
            }
        )

        last_snapshot[pair_addr] = {
            "current_price": current_price,
            "apr": apr,
            "apy": apy,
            "timestamp": now,
        }

    recs.sort(key=lambda item: item["score"], reverse=True)
    recs = recs[: args.top]

    Path("out").mkdir(exist_ok=True)
    out_path = Path("out") / "recommendations.json"
    out_path.write_text(json.dumps(recs, indent=2), encoding="utf-8")

    save_first_seen(first_seen)
    save_last_snapshot(last_snapshot)

    if args.json_only:
        console.print(f"[green]Saved:[/green] {out_path}")
        return

    table = Table(title=f"Meteora LP Ideas (fresh <= {args.days} days)")
    table.add_column("#", justify="right")
    table.add_column("Name", overflow="fold")
    table.add_column("APR", justify="right")
    table.add_column("Fee%", justify="right")
    table.add_column("BinStep", justify="right")
    table.add_column("Vol%", justify="right")
    table.add_column("Age(h)", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Strategy", overflow="fold")
    table.add_column("Hold", overflow="fold")
    table.add_column("Pair Address", overflow="fold")

    for idx, rec in enumerate(recs, start=1):
        table.add_row(
            str(idx),
            rec["name"],
            f'{rec["apr_24h"]:.2f}',
            f'{rec["base_fee_pct"]:.2f}',
            str(rec["bin_step"]),
            f'{rec["vol_pct"]:.2f}',
            f'{rec["age_hours"]:.1f}',
            f'{rec["score"]:.1f}',
            rec["strategy"],
            rec["hold"],
            rec["pair_address"],
        )

    console.print(table)
    console.print(f"[green]Saved JSON:[/green] {out_path}")


if __name__ == "__main__":
    main()
