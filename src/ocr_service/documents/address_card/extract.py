from __future__ import annotations

from typing import Optional, Tuple, List, Pattern, Callable

from ocr_service.core.utils.normalize import parse_dates_iso
from ocr_service.core.utils.extract import (
    find_label_idx,
    find_first_label,
    value_after_match,
    cut_at_next_label,
    is_stop_label,
    scan_forward,
    extract_from_label,
)
from ocr_service.documents.address_card import rules as rr


# ---------------------------
# small helpers
# ---------------------------

def _stop_pred(line: str) -> bool:
    return is_stop_label(line, rr.STOP_LABELS)


def _has_date(s: str) -> bool:
    return bool(parse_dates_iso(s or ""))


def _first_iso_date_in(s: str) -> Optional[str]:
    ds = parse_dates_iso(s or "")
    return ds[0] if ds else None


def _remove_dates(s: str) -> Optional[str]:
    """
    Remove date tokens discovered by parse_dates_iso() from text.
    Used to clean birth_place lines where OCR may mix in dates.
    """
    if not s:
        return None
    tmp = s
    for d in parse_dates_iso(tmp):
        tmp = tmp.replace(d, " ")
        tmp = tmp.replace(d.replace("-", "."), " ")
        # also handle spaced-dot OCR like "1948. 02. 12"
        try:
            y, m, dd = d.split("-")
            tmp = tmp.replace(f"{y}. {m}. {dd}", " ")
        except Exception:
            pass
    cleaned = " ".join((tmp or "").split()).strip()
    return cleaned or None


def _extract_value_line(lines: List[str], label_re: Pattern[str]) -> Optional[str]:
    """
    Label-first extraction:
      - If label line has tail after match, use it.
      - Else use next non-empty line.
      - Cut at next stop label for inline safety.
    """
    hit = find_first_label(lines, label_re)
    if not hit:
        return None
    i, m = hit
    tail = value_after_match(lines[i], m)
    if tail:
        v = cut_at_next_label(tail, rr.STOP_LABELS) or tail
        return v.strip() or None

    nxt = scan_forward(
        lines,
        i,
        stop_pred=_stop_pred,
        skip_pred=None,
        accept_pred=None,  # first non-empty non-stop line
        max_lines=None,
    )
    return nxt.strip() if nxt else None


def _extract_value_2lines(lines: List[str], label_re: Pattern[str]) -> Optional[str]:
    """
    Like _extract_value_line, but appends one continuation line if present.
    """
    hit = find_first_label(lines, label_re)
    if not hit:
        return None
    i, m = hit

    tail = value_after_match(lines[i], m)
    if tail:
        first = (cut_at_next_label(tail, rr.STOP_LABELS) or tail).strip()
        first_idx = i
    else:
        first = scan_forward(lines, i, stop_pred=_stop_pred, accept_pred=None)
        first_idx = i if first is None else (i + 1)

    if not first:
        return None

    nxt = scan_forward(
        lines,
        first_idx,
        stop_pred=_stop_pred,
        accept_pred=lambda s: True,
        max_lines=2,
    )
    if nxt and not _stop_pred(nxt):
        combined = f"{first} {nxt}".strip()
        return combined or first

    return first


def _first_date_after_idx(lines: List[str], start_idx: int, max_lines: int = 6) -> Optional[str]:
    """
    Scan forward a few lines; return the first ISO date found.
    """
    ln = scan_forward(
        lines,
        start_idx,
        stop_pred=_stop_pred,
        accept_pred=_has_date,
        max_lines=max_lines,
    )
    return _first_iso_date_in(ln) if ln else None


# ---------------------------
# extractors
# ---------------------------

def extract_document_number(lines: list[str], full_text: str) -> Optional[str]:
    """
    Best-effort raw candidate. Canonicalization happens in postprocess.py.
    """
    v = extract_from_label(
        lines,
        label_re=rr.TITLE_LABEL,
        stop_label_pats=rr.STOP_LABELS,
        value_re=rr.DOCNO_VALUE,
        fallback_re=rr.DOCNO_VALUE,
        full_text_for_fallback=full_text,
    )
    return v.strip() if v else None


def extract_full_name(lines: list[str]) -> Optional[str]:
    return _extract_value_line(lines, rr.FULL_NAME_LABEL)


def extract_birth_place_and_date(lines: list[str]) -> Tuple[Optional[str], Optional[str]]:
    idx = find_label_idx(lines, rr.BIRTH_PLACE_DATE_LABEL)
    if idx is None:
        return None, None

    # Birth place: label value (same-line tail or next line), remove dates
    birth_place = _extract_value_line(lines, rr.BIRTH_PLACE_DATE_LABEL)
    birth_place = _remove_dates(birth_place) if birth_place else None

    # Append one continuation line (often country), but strip dates from it too
    if birth_place:
        hit = find_first_label(lines, rr.BIRTH_PLACE_DATE_LABEL)
        if hit:
            i, m = hit
            tail = value_after_match(lines[i], m)
            place_line_idx = i  # continuation scan begins after label line

            nxt = scan_forward(
                lines,
                place_line_idx,
                stop_pred=_stop_pred,
                accept_pred=lambda s: True,
                max_lines=3,
            )
            if nxt and not _stop_pred(nxt):
                nxt_clean = _remove_dates(nxt)
                if nxt_clean:
                    birth_place = " ".join(f"{birth_place}, {nxt_clean}".split()).strip() or birth_place

    # Birth date: earliest date on label line preferred, else forward scan
    birth_date = _first_iso_date_in(lines[idx])
    if not birth_date:
        birth_date = _first_date_after_idx(lines, idx, max_lines=6)

    return birth_place, birth_date


def extract_mothers_name(lines: list[str]) -> Optional[str]:
    return _extract_value_line(lines, rr.MOTHERS_NAME_LABEL)


def extract_permanent_address(lines: list[str]) -> Optional[str]:
    return _extract_value_2lines(lines, rr.PERMANENT_ADDRESS_LABEL)


def extract_temporary_address(lines: list[str]) -> Optional[str]:
    return _extract_value_2lines(lines, rr.TEMPORARY_ADDRESS_LABEL)


def _find_reporting_time_idx_between(
    lines: List[str], start_idx: int, end_idx: Optional[int]
) -> Optional[int]:
    end = end_idx if end_idx is not None else len(lines)
    for i in range(start_idx + 1, min(end, len(lines))):
        if rr.REPORTING_TIME_LABEL.search(lines[i]):
            return i
    return None


def extract_permanent_reporting_time(lines: list[str]) -> Optional[str]:
    perm_idx = find_label_idx(lines, rr.PERMANENT_ADDRESS_LABEL)
    if perm_idx is None:
        return None

    temp_idx = find_label_idx(lines, rr.TEMPORARY_ADDRESS_LABEL, start=perm_idx + 1)
    rpt_idx = _find_reporting_time_idx_between(lines, perm_idx, temp_idx)
    if rpt_idx is None:
        return None

    v = _extract_value_line(lines, rr.REPORTING_TIME_LABEL)
    return _first_iso_date_in(v) if v else None


def extract_temporary_reporting_time(lines: list[str]) -> Optional[str]:
    temp_idx = find_label_idx(lines, rr.TEMPORARY_ADDRESS_LABEL)
    if temp_idx is None:
        return None

    val_idx = find_label_idx(lines, rr.VALIDITY_LABEL, start=temp_idx + 1)
    auth_idx = find_label_idx(lines, rr.ISSUING_AUTHORITY_LABEL, start=temp_idx + 1)

    end_idx = None
    for b in (val_idx, auth_idx):
        if b is not None:
            end_idx = b if end_idx is None else min(end_idx, b)

    rpt_idx = _find_reporting_time_idx_between(lines, temp_idx, end_idx)
    if rpt_idx is None:
        return None

    # Anchor using the found index to avoid picking the wrong reporting time
    hit = find_first_label(lines, rr.REPORTING_TIME_LABEL, start=rpt_idx)
    if not hit:
        return None
    i, m = hit

    tail = value_after_match(lines[i], m)
    if tail:
        cand = cut_at_next_label(tail, rr.STOP_LABELS) or tail
        iso = _first_iso_date_in(cand)
        if iso:
            return iso

    nxt = scan_forward(lines, i, stop_pred=_stop_pred, accept_pred=_has_date, max_lines=6)
    return _first_iso_date_in(nxt) if nxt else None


def extract_temporary_validity(lines: list[str]) -> Optional[str]:
    v = _extract_value_line(lines, rr.VALIDITY_LABEL)
    return _first_iso_date_in(v) if v else None


def extract_issuing_authority_and_issue_date(lines: list[str]) -> Tuple[Optional[str], Optional[str]]:
    idx = find_label_idx(lines, rr.ISSUING_AUTHORITY_LABEL)
    if idx is None:
        return None, None

    issuing_authority = _extract_value_line(lines, rr.ISSUING_AUTHORITY_LABEL)

    issue_date = _first_iso_date_in(lines[idx])
    if not issue_date:
        issue_date = _first_date_after_idx(lines, idx, max_lines=6)

    return issuing_authority, issue_date
