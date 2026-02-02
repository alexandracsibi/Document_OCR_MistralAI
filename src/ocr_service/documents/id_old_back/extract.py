from __future__ import annotations

from typing import Iterable, Optional

from ocr_service.core.utils.ocr_text import search_value
from ocr_service.core.utils.extract import norm_lines, nextline_value, nextline_value_guarded
from ocr_service.core.utils.normalize import normalize_sex, parse_dates_iso
from ocr_service.documents.id_old_back import rules as rr


def _get_value(text: str, inline_pat, label_pat) -> Optional[str]:
    """
    Primary: inline 'label: value' (regex match_value)
    Fallback: label -> next non-empty line (guarded against label-as-value)
    """
    text = text or ""

    v = search_value(text, inline_pat)
    if v:
        return v

    lines = norm_lines(text)
    res = nextline_value_guarded(lines, label_pat, rr.STOP_LABELS)
    return res.value


def extract_birth_name(text: str) -> Optional[str]:
    return _get_value(text, rr.BIRTH_NAME_INLINE, rr.BIRTH_NAME_LABEL)


def extract_birth_place(text: str) -> Optional[str]:
    return _get_value(text, rr.BIRTH_PLACE_INLINE, rr.BIRTH_PLACE_LABEL)


def extract_birth_date(text: str) -> Optional[str]:
    raw = _get_value(text, rr.BIRTH_DATE_INLINE, rr.BIRTH_DATE_LABEL)
    if not raw:
        return None
    ds = parse_dates_iso(raw)
    return ds[0] if ds else None


def extract_mothers_name(text: str) -> Optional[str]:
    return _get_value(text, rr.MOTHERS_NAME_INLINE, rr.MOTHERS_NAME_LABEL)


def extract_sex(text: str) -> Optional[str]:
    raw = _get_value(text, rr.SEX_INLINE, rr.SEX_LABEL)
    return normalize_sex(raw or "")


def extract_nationality(text: str) -> Optional[str]:
    raw = search_value(text or "", rr.NATIONALITY_INLINE)
    if not raw:
        return None

    s = raw.strip()
    if "/" in s:
        s = s.split("/")[-1].strip()
    token = s.split()[0].strip(".,;:")
    return token.upper() if token else None


def extract_issuing_authority(text: str) -> Optional[str]:
    raw = search_value(text or "", rr.ISSUING_AUTHORITY_INLINE)
    if not raw:
        return None

    s = raw.strip()

    # strip trailing date-like content by cutting at first year occurrence
    # (can later move to validate.py)
    dates = parse_dates_iso(s)
    if dates:
        year = dates[0][:4]
        idx = s.find(year)
        if idx != -1:
            s = s[:idx].strip()

    return s or None
