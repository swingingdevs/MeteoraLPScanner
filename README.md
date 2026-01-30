# Meteora LP Scanner

A local Python CLI tool to fetch Meteora DLMM pairs, store snapshots, and recommend fresh opportunities.

## Setup

```bash
python -m venv .venv
. .venv/bin/activate  # macOS/Linux
# or on Windows PowerShell:
# .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## One-shot mode

```bash
python -m meteora_lp_scanner --days 3 --top 15
```

## Watch mode

```bash
python -m meteora_lp_scanner --watch --interval 60 --days 3 --top 15
```

## Outputs

- History stored in `./data/first_seen.json` and `./data/snapshots.json`.
- Recommendations saved to `./out/recommendations.json`.
- Table output rendered with Rich unless `--json-only` is provided.

## CLI Flags

- `--days` (default 3): fresh window in days.
- `--top` (default 15): number of recommendations.
- `--min-tvl` (default 0): minimum TVL filter.
- `--min-vol24h` (default 0): minimum 24h volume filter.
- `--min-fees24h` (default 0): minimum 24h fees filter.
- `--new-only` (default false): only pools never seen before on this machine.
- `--json-only` (default false): skip table output.
- `--watch` (default false): poll repeatedly.
- `--interval` (default 60): watch mode interval in seconds.
