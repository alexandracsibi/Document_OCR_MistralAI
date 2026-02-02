from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional, Pattern, Sequence, Tuple, TypeVar

from ocr_service.core.utils.ocr_text import normalize_ocr_line, split_lines, next_non_empty

T = TypeVar("T")


# ---------------------------
# Lines
# ---------------------------

def norm_lines(text: str) -> list[str]:
    """
    Split -> normalize -> strip -> drop empties.
    No document-specific truncation (e.g., C-block) here.
    """
    out: list[str] = []
    for ln in split_lines(text or ""):
        ln2 = normalize_ocr_line(ln)
        if not ln2:
            continue
        ln2 = ln2.strip()
        if ln2:
            out.append(ln2)
    return out


# ---------------------------
# Label finding
# ---------------------------

def find_first_label(
    lines: Sequence[str],
    label_re: Pattern[str],
    start: int = 0,
) -> Optional[Tuple[int, Any]]:
    """
    Return (index, match) for the first occurrence of label_re in lines[start:].
    """
    for i in range(max(0, start), len(lines)):
        m = label_re.search(lines[i] or "")
        if m:
            return i, m
    return None


def find_label_idx(
    lines: Sequence[str],
    label_re: Pattern[str],
    start: int = 0,
) -> Optional[int]:
    hit = find_first_label(lines, label_re, start=start)
    return hit[0] if hit else None


# ---------------------------
# Value slicing helpers
# ---------------------------

def value_after_match(line: str, m: Any, *, strip_prefix_chars: str = ":. ") -> str:
    """
    Return text after the matched label, trimming common separators.
    """
    tail = (line[m.end():] or "").strip()
    while tail and tail[0] in strip_prefix_chars:
        tail = tail[1:].lstrip()
    return tail.strip()


def value_after_colon(line: str, *, start_pos: int = 0) -> Optional[str]:
    """
    Return normalized tail after the first ':' at/after start_pos.
    """
    if not line:
        return None
    pos = line.find(":", start_pos)
    if pos == -1:
        return None
    v = normalize_ocr_line(line[pos + 1 :])
    v = v.strip() if v else ""
    return v or None


def cut_at_next_label(remainder: str, stop_label_pats: Sequence[Pattern[str]]) -> str:
    """
    Cut 'remainder' at the earliest stop-label match.
    stop_label_pats must be inline-capable if you want mid-line cutting.
    """
    if not remainder:
        return ""
    cut = len(remainder)
    for p in stop_label_pats:
        ms = p.search(remainder)
        if ms:
            cut = min(cut, ms.start())
    return remainder[:cut].strip()


# ---------------------------
# Stop / scan utilities
# ---------------------------

def is_stop_label(line: str, stop_label_pats: Sequence[Pattern[str]]) -> bool:
    s = line or ""
    return any(p.search(s) for p in stop_label_pats)


def nextline_value(
    lines: Sequence[str],
    label_pat: Pattern[str],
) -> Optional[str]:
    """
    Return next_non_empty after the first line containing label_pat.
    """
    hit = find_first_label(lines, label_pat)
    if not hit:
        return None
    i, _ = hit
    return next_non_empty(lines, i)


@dataclass(frozen=True)
class GuardedNextlineResult:
    value: Optional[str]
    found_label: bool
    blocked_by_stop: bool


def nextline_value_guarded(
    lines: Sequence[str],
    label_pat: Pattern[str],
    stop_label_pats: Sequence[Pattern[str]],
) -> GuardedNextlineResult:
    """
    Like nextline_value, but blocks if the next non-empty line matches any stop label.
    Returns more detail to let callers distinguish "label missing" vs "blocked".
    """
    hit = find_first_label(lines, label_pat)
    if not hit:
        return GuardedNextlineResult(value=None, found_label=False, blocked_by_stop=False)

    i, _ = hit
    v = next_non_empty(lines, i)
    if not v:
        return GuardedNextlineResult(value=None, found_label=True, blocked_by_stop=False)

    if is_stop_label(v, stop_label_pats):
        return GuardedNextlineResult(value=None, found_label=True, blocked_by_stop=True)

    return GuardedNextlineResult(value=v, found_label=True, blocked_by_stop=False)


def scan_forward(
    lines: Sequence[str],
    start_idx: int,
    *,
    stop_pred: Callable[[str], bool],
    skip_pred: Optional[Callable[[str], bool]] = None,
    accept_pred: Optional[Callable[[str], bool]] = None,
    max_lines: Optional[int] = None,
) -> Optional[str]:
    """
    Scan forward from start_idx+1 and return the first line that is accepted.

    - stops if stop_pred(line) is True
    - skips if skip_pred(line) is True
    - accepts if accept_pred(line) is True (or accepts first non-empty line if accept_pred is None)
    """
    end = len(lines) if max_lines is None else min(len(lines), start_idx + 1 + max_lines)
    j = start_idx + 1
    while j < end:
        cur = (lines[j] or "").strip()
        if not cur:
            j += 1
            continue
        if stop_pred(cur):
            return None
        if skip_pred is not None and skip_pred(cur):
            j += 1
            continue
        if accept_pred is None or accept_pred(cur):
            return cur
        j += 1
    return None


# ---------------------------
# Fallback
# ---------------------------

def fallback_value(text: str, value_re: Pattern[str]) -> Optional[str]:
    """
    Global fallback: search over normalized whole text.
    Returns group(1) if present else group(0).
    """
    s = normalize_ocr_line(text or "") or (text or "")
    m = value_re.search(s)
    if not m:
        return None
    if m.lastindex and m.lastindex >= 1:
        return (m.group(1) or "").strip() or None
    return (m.group(0) or "").strip() or None


# ---------------------------
# Main primitive
# ---------------------------

def extract_from_label(
    lines: Sequence[str],
    *,
    label_re: Pattern[str],
    stop_label_pats: Sequence[Pattern[str]],
    value_re: Optional[Pattern[str]] = None,
    validator: Optional[Callable[[str], bool]] = None,
    fallback_re: Optional[Pattern[str]] = None,
    full_text_for_fallback: Optional[str] = None,
    skip_pred: Optional[Callable[[str], bool]] = None,
) -> Optional[str]:
    """
    Core extraction primitive (document-agnostic).

    Strategy:
      1) Find first label occurrence in `lines`.
      2) Candidate from same line: tail after match; cut at next stop label; validate.
      3) If not accepted: scan forward line-by-line until stop label; validate each; return first accepted.
      4) If still not found and fallback_re provided: run fallback_re on full_text_for_fallback.

    Notes:
      - stop_label_pats are used both for inline cutting and for stopping forward scan.
      - skip_pred can suppress certain lines (e.g., C-block lines) from being used as values.
      - If you want fallback, you MUST pass full_text_for_fallback (usually original ocr.text).
    """
    def ok(s: str) -> bool:
        if not s:
            return False
        if validator is not None and not validator(s):
            return False
        if value_re is not None and not value_re.search(s):
            return False
        return True

    hit = find_first_label(lines, label_re)
    if not hit:
        if fallback_re is not None and full_text_for_fallback is not None:
            return fallback_value(full_text_for_fallback, fallback_re)
        return None

    i, m = hit
    remainder = value_after_match(lines[i], m)

    # same-line candidate
    if remainder:
        cand = cut_at_next_label(remainder, stop_label_pats) or remainder
        if ok(cand):
            return cand

    # forward scan until stop
    stop_pred = lambda s: is_stop_label(s, stop_label_pats)
    v = scan_forward(
        lines,
        i,
        stop_pred=stop_pred,
        skip_pred=skip_pred,
        accept_pred=ok,
        max_lines=None,
    )
    if v is not None:
        return v

    # fallback
    if fallback_re is not None and full_text_for_fallback is not None:
        return fallback_value(full_text_for_fallback, fallback_re)

    return None
