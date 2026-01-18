# Meteora LP Scanner

A local Python CLI tool to fetch Meteora DLMM pairs, track first-seen history, score pools, and recommend fresh opportunities.

## Setup (Windows-friendly)

```bash
cd meteora_lp_scanner
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

### Example runs

```bash
python main.py --days 2 --top 10
python main.py --min-apr 50 --new-only
python main.py --json-only
```

## Outputs

- History stored in `./data/first_seen.json` and `./data/last_snapshot.json`.
- Recommendations saved to `./out/recommendations.json`.
- Table output rendered with Rich unless `--json-only` is provided.

## CLI Flags

- `--days` (default 3): fresh window in days.
- `--top` (default 15): number of recommendations.
- `--min-apr` (default 0): filter by minimum APR.
- `--new-only` (default false): only pools never seen before on this machine.
- `--json-only` (default false): skip table output.
