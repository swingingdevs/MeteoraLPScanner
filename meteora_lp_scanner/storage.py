import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")
OUT_DIR = Path("out")

FIRST_SEEN_FILE = DATA_DIR / "first_seen.json"
SNAPSHOTS_FILE = DATA_DIR / "snapshots.json"


def ensure_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)


def _load_json(path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save_json(path, obj):
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def load_first_seen():
    ensure_dirs()
    return _load_json(FIRST_SEEN_FILE, {})


def save_first_seen(first_seen_map):
    ensure_dirs()
    _save_json(FIRST_SEEN_FILE, first_seen_map)


def load_snapshots():
    ensure_dirs()
    return _load_json(SNAPSHOTS_FILE, {})


def save_snapshots(snapshot_map):
    ensure_dirs()
    _save_json(SNAPSHOTS_FILE, snapshot_map)


def now_iso():
    return datetime.now(timezone.utc).isoformat()
