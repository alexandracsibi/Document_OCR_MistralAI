from typing import Optional

from ocr_service.core.utils.extract import norm_lines, nextline_value
from ocr_service.core.utils.ocr_text import search_value
from ocr_service.core.utils.normalize import parse_dates_iso, normalize_id_number

from ocr_service.documents.id_old_front import rules as rr


def extract_full_name(text: str) -> Optional[str]:
    """
    Label -> next non-empty line.
    """
    lines = norm_lines(text or "")
    return nextline_value(lines, rr.NAME_LABEL)


def extract_expiry_date(text: str) -> Optional[str]:
    """
    Old HU ID front: expiry date is typically the only meaningful date.
    """
    ds = parse_dates_iso(text or "")
    return ds[-1] if ds else None


def extract_document_number(text: str) -> Optional[str]:
    """
    Prefer inline docno label; fallback to candidate scan.
    Returns normalized doc number (6 digits + 2 letters) or None.
    """
    text = text or ""

    # 1) inline
    v = search_value(text, rr.DOCNO_INLINE)
    if v:
        token = v.split()[0].strip(".,;:")
        norm = normalize_id_number(token)
        if norm:
            return norm

    # 2) fallback scan (keep boundaries; remove all whitespace safely)
    compact = " ".join(text.split())
    for m in rr.ID_NUMBER_CANDIDATE.finditer(compact):
        raw = m.group(1)
        norm = normalize_id_number(raw)
        if norm:
            return norm

    return None
