import argparse
import json
import time
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .recommend import ScannerConfig, get_recommendations
from .storage import ensure_dirs, OUT_DIR


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Meteora DLMM LP Scanner")
    parser.add_argument("--days", type=float, default=3.0)
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--min-tvl", type=float, default=0.0)
    parser.add_argument("--min-vol24h", type=float, default=0.0)
    parser.add_argument("--min-fees24h", type=float, default=0.0)
    parser.add_argument("--new-only", action="store_true")
    parser.add_argument("--json-only", action="store_true")
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--interval", type=int, default=60)
    return parser


def render_table(recs, days):
    table = Table(title=f"Meteora LP Ideas (fresh <= {days} days)")
    table.add_column("#", justify="right")
    table.add_column("Name", overflow="fold")
    table.add_column("TVL", justify="right")
    table.add_column("Vol24h", justify="right")
    table.add_column("Fees24h", justify="right")
    table.add_column("Vol/min", justify="right")
    table.add_column("Fees/min", justify="right")
    table.add_column("Move%", justify="right")
    table.add_column("Age(h)", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Strategy", overflow="fold")
    table.add_column("Hold", overflow="fold")
    table.add_column("Pair Address", overflow="fold")

    for idx, rec in enumerate(recs, start=1):
        table.add_row(
            str(idx),
            rec["name"],
            f'{rec["tvl"]:,.2f}',
            f'{rec["volume_24h"]:,.2f}',
            f'{rec["fees_24h"]:,.2f}',
            f'{rec["vol_per_min"]:,.2f}',
            f'{rec["fees_per_min"]:,.2f}',
            f'{rec["move_pct"]:,.2f}',
            f'{rec["age_hours"]:.1f}',
            f'{rec["score"]:.1f}',
            rec["strategy"],
            rec["hold"],
            rec["pair_address"],
        )

    return table


def run_once(config: ScannerConfig, json_only: bool, console: Console) -> Path:
    ensure_dirs()
    recs = get_recommendations(config)
    out_path = OUT_DIR / "recommendations.json"
    out_path.write_text(json.dumps(recs, indent=2), encoding="utf-8")

    if json_only:
        console.print(f"[green]Saved JSON:[/green] {out_path}")
        return out_path

    table = render_table(recs, config.days)
    console.print(table)
    console.print(f"[green]Saved JSON:[/green] {out_path}")
    return out_path


def main():
    parser = build_parser()
    args = parser.parse_args()

    config = ScannerConfig(
        days=args.days,
        top=args.top,
        min_tvl=args.min_tvl,
        min_vol24h=args.min_vol24h,
        min_fees24h=args.min_fees24h,
        new_only=args.new_only,
    )

    console = Console()

    if args.watch:
        console.print(
            f"[cyan]Watch mode:[/cyan] every {args.interval}s | days={args.days} top={args.top}"
        )
        try:
            while True:
                run_once(config, args.json_only, console)
                time.sleep(max(1, args.interval))
        except KeyboardInterrupt:
            console.print("[yellow]Stopped watch mode.[/yellow]")
    else:
        run_once(config, args.json_only, console)


if __name__ == "__main__":
    main()
