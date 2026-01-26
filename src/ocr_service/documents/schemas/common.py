from __future__ import annotations

def empty_fields(keys: list[str]) -> dict[str, object]:
    return {k: None for k in keys}
