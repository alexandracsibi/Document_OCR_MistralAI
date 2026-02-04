from __future__ import annotations

from datetime import date
import html
import re
from typing import List, Optional, Match, Pattern, Tuple

_MD_DECOR = re.compile(r"[*_`#>]+")  # basic markdown tokens
_MRZ_ALLOWED = re.compile(r"[^A-Z0-9<]")


def _mrz_clean(line: str) -> str:
    # decode '&lt;' -> '<' etc.
    s = html.unescape(line or "")
    s = s.upper()
    s = s.replace(" ", "")
    s = s.replace("«", "<").replace("‹", "<").replace("›", "<")
    s = _MRZ_ALLOWED.sub("", s)
    return s

def _is_mrzish(s: str) -> bool:
    if not s:
        return False
    return 20 <= len(s) <= 40

def _pad_or_trim_30(s: str) -> str:
    if len(s) >= 30:
        return s[:30]
    return s + ("<" * (30 - len(s)))

def _mrz_value(ch: str) -> int:
    # ICAO 9303 character values
    if "0" <= ch <= "9":
        return ord(ch) - ord("0")
    if "A" <= ch <= "Z":
        return ord(ch) - ord("A") + 10
    if ch == "<":
        return 0
    return 0

def mrz_check_digit(field: str) -> str:
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(field):
        total += _mrz_value(ch) * weights[i % 3]
    return str(total % 10)

def find_mrz_td1_block(lines: List[str]) -> Optional[Tuple[str, str, str]]:
    """
    Find best consecutive triple of MRZ-ish lines.
    Returns 3 lines, each exactly 30 chars (padded/trimmed).
    """
    cleaned = [(_mrz_clean(ln), i) for i, ln in enumerate(lines)]
    cand = [(s, i) for (s, i) in cleaned if _is_mrzish(s)]

    # try consecutive triples (by original line index)
    best: Optional[Tuple[int, Tuple[str, str, str]]] = None

    cand_by_idx = {i: s for (s, i) in cand}
    for i in range(len(lines) - 2):
        if i not in cand_by_idx or (i + 1) not in cand_by_idx or (i + 2) not in cand_by_idx:
            continue

        l1 = _pad_or_trim_30(cand_by_idx[i])
        l2 = _pad_or_trim_30(cand_by_idx[i + 1])
        l3 = _pad_or_trim_30(cand_by_idx[i + 2])

        # Simple scoring: closeness to 30 before pad + check digits validity if possible
        score = 0
        score -= abs(len(cand_by_idx[i]) - 30)
        score -= abs(len(cand_by_idx[i + 1]) - 30)
        score -= abs(len(cand_by_idx[i + 2]) - 30)

        # bonus if DOB check digit matches
        dob = l2[0:6]
        dob_cd = l2[6:7]
        if re.fullmatch(r"\d{6}", dob) and dob_cd.isdigit():
            if mrz_check_digit(dob) == dob_cd:
                score += 5

        if best is None or score > best[0]:
            best = (score, (l1, l2, l3))

    return best[1] if best else None

def parse_mrz_birth_date_yyMMdd(token: str, *, today: Optional[date] = None) -> Optional[str]:
    """
    Convert YYMMDD -> YYYY-MM-DD with a deterministic century rule:
    - if YY > current_year%100 => 1900+YY else 2000+YY
    """
    if not token or not re.fullmatch(r"\d{6}", token):
        return None
    yy = int(token[0:2])
    mm = int(token[2:4])
    dd = int(token[4:6])

    today = today or date.today()
    pivot = today.year % 100
    year = 1900 + yy if yy > pivot else 2000 + yy

    try:
        d = date(year, mm, dd)
    except ValueError:
        return None
    return d.isoformat()


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