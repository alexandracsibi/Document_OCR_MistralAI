from __future__ import annotations
import re
from typing import Optional, List
from datetime import date
from ocr_service.core.utils import rules

def _safe_date(y: int, m: int, d: int) -> Optional[date]:
    try:
        return date(y, m, d)
    except ValueError:
        return None
    
def _month_token_to_num(token: str) -> Optional[int]:
    t = (token or "").strip().lower()
    t = t[:-1] if t.endswith(".") else t
    return rules.MONTH_MAP.get(t) or rules.MONTH_MAP.get(t + ".")

def parse_dates_iso(text: Optional[str]) -> List[str]:
    """
    Parse all date-like tokens from text and return unique valid dates in ISO format,
    sorted ascending.

    This function is document-agnostic. Document-specific logic (which date matters)
    must be handled in the document extractor/processor.
    """
    if not text:
        return []

    found: set[date] = set()

    for m in rules.DATE_DDMMYYYY.finditer(text):
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        dt = _safe_date(y, mo, d)
        if dt:
            found.add(dt)

    for m in rules.DATE_YYYYMMDD.finditer(text):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        dt = _safe_date(y, mo, d)
        if dt:
            found.add(dt)

    for m in rules.DATE_YYYY_MON_DD.finditer(text):
        y = int(m.group(1))
        mon_token = m.group(2)
        d = int(m.group(3))

        parts = [p.strip() for p in mon_token.split("/") if p.strip()]
        month_num: Optional[int] = None
        for p in parts:
            month_num = _month_token_to_num(p)
            if month_num is not None:
                break
        if month_num is None:
            continue

        dt = _safe_date(y, month_num, d)
        if dt:
            found.add(dt)

    for m in rules.DATE_YYYY_HU_MON_DD.finditer(text):
        y = int(m.group(1))
        mon_token = m.group(2)
        d = int(m.group(3))

        month_num = _month_token_to_num(mon_token)
        if month_num is None:
            continue

        dt = _safe_date(y, month_num, d)
        if dt:
            found.add(dt)

    for m in rules.DATE_DD_MON_YY.finditer(text):
        d = int(m.group(1))
        mon_token = m.group(2)
        yy = int(m.group(3))

        parts = [p.strip() for p in mon_token.split("/") if p.strip()]
        month_num = None
        for p in parts:
            month_num = _month_token_to_num(p)
            if month_num is not None:
                break
        if month_num is None:
            continue
        # 00-49 => 2000-2049
        # 50-99 => 1950-1999
        y = 2000 + yy if yy <= 49 else 1900 + yy

        dt = _safe_date(y, month_num, d)
        if dt:
            found.add(dt)

    return [dt.isoformat() for dt in sorted(found)]

def ddmmyy_from_iso(iso_date: str) -> Optional[str]:
    """
    'YYYY-MM-DD' -> 'DDMMYY'
    """
    if not iso_date:
        return None
    try:
        yyyy, mm, dd = iso_date.split("-")
        return f"{dd}{mm}{yyyy[-2:]}"
    except Exception:
        return None
    

def normalize_sex(raw: str) -> Optional[str]:
    """
    Output: 'NŐ' or 'FÉRFI'

    Accepts OCR variants:
      Female: NŐ, NÓ, NO, N/F
      Male: FÉRFI, FERFI, F, M, F/M
    """
    if not raw:
        return None

    u = raw.upper().strip()

    # Normalize common OCR diacritic error: Ő -> Ó
    u = u.replace("Ő", "Ó")

    # tokenize safely (avoid substring accidents)
    tokens = re.findall(r"[A-ZÓŐ]+", u)

    # female indicators
    if any(t in {"NŐ", "NÓ", "NO"} for t in tokens) or "N/F" in u:
        return "NŐ"

    # male indicators
    if any(t in {"FÉRFI", "FERFI", "F", "M"} for t in tokens) or "F/M" in u:
        return "FÉRFI"

    return None