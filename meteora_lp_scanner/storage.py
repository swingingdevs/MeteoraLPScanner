import json
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path("data")
OUT_DIR = Path("out")

FIRST_SEEN_FILE = DATA_DIR / "first_seen.json"
LAST_SNAPSHOT_FILE = DATA_DIR / "last_snapshot.json"


def _ensure_dirs():
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
    _ensure_dirs()
    return _load_json(FIRST_SEEN_FILE, {})


def save_first_seen(first_seen_map):
    _ensure_dirs()
    _save_json(FIRST_SEEN_FILE, first_seen_map)


def load_last_snapshot():
    _ensure_dirs()
    return _load_json(LAST_SNAPSHOT_FILE, {})


def save_last_snapshot(snapshot_map):
    _ensure_dirs()
    _save_json(LAST_SNAPSHOT_FILE, snapshot_map)


def now_iso():
    return datetime.now(timezone.utc).isoformat()
