from __future__ import annotations

from typing import Optional, Tuple

from ocr_service.core.utils.extract import nextline_value, norm_lines
from ocr_service.core.utils.ocr_text import search_value
from ocr_service.core.utils.normalize import (
    parse_dates_iso,
    ddmmyy_from_iso,
    normalize_sex,
)
from ocr_service.documents.id_front import rules as rr
from ocr_service.documents.id_front.normalize import normalize_id_number


def _first_token(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    t = s.split()[0].strip(".,;:")
    return t or None


def extract_full_name(text: str) -> Optional[str]:
    lines = norm_lines(text)
    return nextline_value(lines, rr.NAME_LABEL)


def extract_sex(text: str) -> Optional[str]:
    """
    Prefer inline KV; fallback to token scan; returns normalized value:
    - 'NŐ' or 'FÉRFI' or None
    """
    text = text or ""
    v = search_value(text, rr.SEX_INLINE)
    if not v:
        m = rr.SEX_TOKEN.search(text)
        v = m.group(0) if m else None
    return normalize_sex(v)


def extract_nationality(text: str) -> Optional[str]:
    """
    Prefer inline KV; fallback to token scan.
    Returns uppercase token (not validated).
    """
    text = text or ""
    v = search_value(text, rr.NATIONALITY_INLINE)
    tok = _first_token(v)
    if tok:
        return tok.upper()

    m = rr.NATIONALITY_TOKEN.search(text)
    return m.group(0).upper() if m else None


def extract_birth_and_expiry_dates(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Generic fallback for HU ID front:
    earliest date => birth_date
    latest date   => expiry_date
    """
    text = text or ""
    dates = parse_dates_iso(text)
    if not dates:
        return None, None
    if len(dates) == 1:
        return dates[0], None
    return dates[0], dates[-1]


def _is_date_derived(norm_id: str, birth_iso: Optional[str], expiry_iso: Optional[str]) -> bool:
    """
    Reject doc-number candidates that are clearly derived from DOB/DOE (DDMMYY prefix).
    """
    if not norm_id:
        return False

    first6 = norm_id[:6]
    dob = ddmmyy_from_iso(birth_iso)
    doe = ddmmyy_from_iso(expiry_iso)

    return (dob is not None and first6 == dob) or (doe is not None and first6 == doe)


def extract_document_number(
    text: str,
    birth_iso: Optional[str],
    expiry_iso: Optional[str],
) -> Optional[str]:
    """
    Prefer inline docno label; fallback to scanning candidates.
    Returns normalized doc number or None.
    """
    text = text or ""
    # 1) inline
    v = search_value(text, rr.DOCNO_INLINE)
    tok = _first_token(v)
    if tok:
        norm = normalize_id_number(tok)
        if norm and not _is_date_derived(norm, birth_iso, expiry_iso):
            return norm

    # 2) scan fallback (remove spaces for OCR split artifacts)
    compact = " ".join(text.split())
    for m in rr.ID_NUMBER_CANDIDATE.finditer(compact):
        raw = m.group(1)
        norm = normalize_id_number(raw)
        if not norm:
            continue
        if _is_date_derived(norm, birth_iso, expiry_iso):
            continue
        return norm

    return None
