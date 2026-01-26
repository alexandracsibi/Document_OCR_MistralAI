from __future__ import annotations
import re
from typing import Optional, Pattern, Match, Iterable

_MD_DECOR = re.compile(r"[*_`#>]+")  # basic markdown tokens

def normalize_whitespace(s: str) -> str:
    return " ".join((s or "").strip().split())

def strip_markdown(s: str) -> str:
    """
    Remove common markdown decoration tokens like '#', '**', '*', '`'.
    Keeps the actual text content.
    """
    if not s:
        return s
    s = s.strip()
    s = _MD_DECOR.sub("", s)
    return normalize_whitespace(s)

def normalize_dl_label(label: str) -> str:
    """
    Normalize label tokens:
      "4(a)" / "4 (a)" / "4a" -> "4a"
      "1" -> "1"
    """
    if not label:
        return label
    s = normalize_whitespace(label)
    s = s.replace("(", "").replace(")", "")
    s = s.replace(" ", "")
    s = s.lower()
    return s

def split_lines(text: str) -> list[str]:
    """
    Split OCR markdown/text into non-empty, whitespace-normalized lines.
    """
    if not text:
        return []
    out: list[str] = []
    for ln in text.splitlines():
        ln2 = normalize_whitespace(ln)
        if ln2:
            out.append(ln2)
    return out

def next_non_empty(lines: list[str], start_idx: int) -> Optional[str]:
    """
    Return the immediate next non-empty line after start_idx (no multi-line lookahead).
    """
    for i in range(start_idx + 1, len(lines)):
        if lines[i].strip():
            return lines[i]
    return None

def _extract_value_from_match(m: Match[str]) -> Optional[str]:
    """
    Prefer named group 'value'. If not present, use the last capturing group.
    """
    if not m:
        return None

    gd = m.groupdict()
    if "value" in gd:
        v = gd.get("value")
        v = strip_markdown(v) if isinstance(v, str) else None
        return v if v else None

    # fallback: last group
    if m.lastindex:
        v = m.group(m.lastindex)
        v = strip_markdown(v) if isinstance(v, str) else None
        return v if v else None

    return None


def extract_inline_value(text: str, pattern: Pattern[str]) -> Optional[str]:
    """
    Search the full text (MULTILINE patterns supported).
    Expects pattern to include (?P<value>...) or at least one capture group for value.
    """
    m = pattern.search(text or "")
    return _extract_value_from_match(m)


def extract_inline_value_from_lines(lines: list[str], pattern: Pattern[str]) -> Optional[str]:
    """
    Search per-line. Useful when you want to avoid cross-line greediness.
    Expects (?P<value>...) group.
    """
    for ln in lines:
        m = pattern.search(ln)
        v = _extract_value_from_match(m)
        if v:
            return v
    return None

def extract_inline_separate_values(lines: list[str], pattern: Pattern[str]) -> Optional[str]:
    """
    Search per-line. Return all separate values found.
    Expects (?P<value>...) group.
    """
    out: list[str] = []
    for ln in lines:
        m = pattern.search(ln)
        v = _extract_value_from_match(m)
        if v:
            out.append(v)
    return out

def extract_nextline_value_guarded(
    lines: list[str],
    label_pattern: Pattern[str],
    stop_label_patterns: Iterable[Pattern[str]],
) -> Optional[str]:
    """
    Like extract_nextline_value, but will NOT return a line that looks like another label.
    If the next non-empty line matches any stop label pattern, returns None.
    """
    for i, ln in enumerate(lines):
        if label_pattern.search(ln):
            v = next_non_empty(lines, i)
            if not v:
                return None
            v = strip_markdown(v)
            for p in stop_label_patterns:
                if p.search(v):
                    return None
            return v
    return None

def extract_nextline_value(lines: list[str], label_pattern: Pattern[str]) -> Optional[str]:
    """
    Find a label line and return the immediate next non-empty line as the value.
    """
    for i, ln in enumerate(lines):
        if label_pattern.search(ln):
            v = next_non_empty(lines, i)
            return strip_markdown(v) if v else None
    return None

def extract_kv_pairs_from_line(
    line: str,
    anchor_pattern: Pattern[str],
) -> List[Tuple[str, str]]:
    """
    Extract multiple (label, value) pairs from a single line using an 'anchor finder' regex.

    Example:
      line: "4a. 03.07.2020 4c. SRPCIV HARGHITA"
      -> [("4a","03.07.2020"), ("4c","SRPCIV HARGHITA")]
    """
    s = normalize_line_for_kv(line)
    if not s:
        return []

    matches = list(anchor_pattern.finditer(s))
    if not matches:
        return []

    pairs: List[Tuple[str, str]] = []
    for i, m in enumerate(matches):
        raw_label = m.group("label")
        key = normalize_dl_label(raw_label)

        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(s)
        val = s[start:end].strip()

        # trim common separators
        val = val.strip(" -–—·|")
        val = normalize_whitespace(val)

        if val:
            pairs.append((key, val))

    return pairs


def extract_kv_pairs_from_lines(
    lines: List[str],
    anchor_pattern: Pattern[str],
    prefer: str = "first",
) -> Dict[str, str]:
    """
    Merge key-value pairs across all lines.

    prefer:
      - "first": first non-empty wins
      - "last": last non-empty wins
      - "longest": longer string wins (useful if OCR repeats partials)
    """
    out: Dict[str, str] = {}

    def choose(existing: Optional[str], new: str) -> str:
        if not existing:
            return new
        if prefer == "last":
            return new
        if prefer == "longest":
            return new if len(new) > len(existing) else existing
        # default "first"
        return existing

    for ln in lines:
        for k, v in extract_kv_pairs_from_line(ln, anchor_pattern):
            out[k] = choose(out.get(k), v)

    return out


def split_birth_date_and_place(raw_3: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    raw_3 is typically: "<date> <place...>"
    Returns (birth_date_iso, birth_place).

    Uses extract_dates() which returns sorted ISO strings.
    """
    if not raw_3:
        return None, None

    s = normalize_line_for_kv(raw_3)
    if not s:
        return None, None

    ds = extract_dates(s)
    birth_date = ds[0] if ds else None
    if not birth_date:
        return None, s

    # Remove common date tokens from the original string (OCR forms),
    # then normalize remaining as place.
    s2 = re.sub(r"\b\d{4}[.\-/]\d{2}[.\-/]\d{2}\b", " ", s)  # YYYY.MM.DD
    s2 = re.sub(r"\b\d{2}[.\-/]\d{2}[.\-/]\d{4}\b", " ", s)  # DD.MM.YYYY
    s2 = normalize_whitespace(s2)

    return birth_date, (s2 or None)
