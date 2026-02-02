from __future__ import annotations

import re
from typing import Optional, Match, Pattern

_MD_DECOR = re.compile(r"[*_`#>]+")  # basic markdown tokens

def normalize_ocr_line(s: str) -> str:
    """
    Normalize a single OCR line:
    - remove basic markdown decoration tokens
    - strip + collapse whitespace
    Always returns a string (possibly empty).
    """
    s = s or ""
    s = _MD_DECOR.sub("", s)
    return " ".join(s.strip().split())

def split_lines(text: str) -> list[str]:
    """
    Split OCR text/markdown into non-empty normalized lines.
    """
    if not text:
        return []
    out: list[str] = []
    for ln in text.splitlines():
        ln2 = normalize_ocr_line(ln)
        if ln2:
            out.append(ln2)
    return out


def next_non_empty(lines: list[str], start_idx: int) -> Optional[str]:
    """
    Return the immediate next non-empty line after start_idx.
    Assumes 'lines' are already normalized (e.g., from split_lines()).
    """
    for i in range(start_idx + 1, len(lines)):
        v = lines[i].strip()
        if v:
            return v
    return None

def match_value(m: Optional[Match[str]]) -> Optional[str]:
    """
    Extract a value from a regex match:
    - prefer named group 'value'
    - otherwise use the last capturing group
    Returns stripped string or None.
    """
    if not m:
        return None

    gd = m.groupdict()
    if "value" in gd:
        return normalize_ocr_line(gd.get("value") or "") or None

    if m.lastindex:
        return normalize_ocr_line(m.group(m.lastindex) or "") or None

    return None


def search_value(text: str, pattern: Pattern[str]) -> Optional[str]:
    """
    Search pattern in text and return extracted value using match_value().
    Pattern should contain (?P<value>...) or at least one capturing group.
    """
    return match_value(pattern.search(text or ""))