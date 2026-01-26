from __future__ import annotations
import json
import hashlib
from pathlib import Path
from typing import Any, Optional

def _safe_filename(key: str) -> str:
    # Windows-safe filename
    return hashlib.sha256(key.encode("utf-8")).hexdigest() + ".json"

def _path(cache_dir: str, key: str) -> Path:
    return Path(cache_dir) / _safe_filename(key)

def load_cached_ocr(cache_dir: str, key: str) -> Optional[dict[str, Any]]:
    p = _path(cache_dir, key)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))

def save_cached_ocr(cache_dir: str, key: str, raw: dict[str, Any]) -> None:
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    p = _path(cache_dir, key)
    p.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
