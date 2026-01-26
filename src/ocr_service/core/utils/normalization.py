from __future__ import annotations
from datetime import date
from typing import Optional, List
from ocr_service.core.utils import patterns

def _safe_date(y: int, m: int, d: int) -> Optional[date]:
    try:
        return date(y, m, d)
    except ValueError:
        return None

def _month_token_to_num(token: str) -> Optional[int]:
    t = token.strip().lower()
    # remove trailing dot from parts if present
    t = t[:-1] if t.endswith(".") else t
    return patterns.MONTH_MAP.get(t) or patterns.MONTH_MAP.get(t + ".")

def extract_dates(text: str) -> List[str]:
    if not text:
        return []
    found: set[date] = set()

    for m in patterns.DATE_DDMMYYYY.finditer(text):
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        dt = _safe_date(y, mo, d)
        if dt: found.add(dt)

    for m in patterns.DATE_YYYYMMDD.finditer(text):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        dt = _safe_date(y, mo, d)
        if dt: found.add(dt)

    for m in patterns.DATE_YYYY_MON_DD.finditer(text):
        y = int(m.group(1))
        mon_token = m.group(2)
        d = int(m.group(3))

        # "Júl/Jul" => try each part
        parts = [p.strip() for p in mon_token.split("/") if p.strip()]
        month_num = None
        for p in parts:
            month_num = _month_token_to_num(p)
            if month_num is not None:
                break
        if month_num is None:
            continue

        dt = _safe_date(y, month_num, d)
        if dt: found.add(dt)

    return [d.isoformat() for d in sorted(found)]

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
    Accepted OCR tokens: N/F, Nő/F, F/M, Férfi/M, plus common variants.
    """
    if not raw:
        return None
    u = raw.upper()

    # female indicators
    if "N/F" in u or "NŐ" in u or " NO" in f" {u} " or " N " in f" {u} ":
        return "NŐ"
    # male indicators
    if "FÉRFI" in u or "FERFI" in u or " M " in f" {u} " or " F " in f" {u} ":
        return "FÉRFI"
    
    return None

def normalize_id_number(raw: str) -> Optional[str]:
    """
    Target format: 6 digits + 2 uppercase letters.

    Correct common OCR confusions:
      digits part: O->0, I/l/|->1
      letters part: 0->O, 1/l/|->I
    """
    if not raw:
        return None
    
    s = raw.strip().upper().replace(" ", "")

    # NOTE if 2 letter became 1 due to OCR error, cannot fix reliably
    if len(s) != 8:
        return None

    first6 = list(s[:6])
    last2 = list(s[6:])

    # digits part
    for i, ch in enumerate(first6):
        if ch == "O":
            first6[i] = "0"
        elif ch in ("I", "L", "|"):
            first6[i] = "1"
        # lowercase l would already become 'L' by upper()

    digits = "".join(first6)
    if not digits.isdigit():
        return None

    # letters part
    for i, ch in enumerate(last2):
        if ch == "0":
            last2[i] = "O"
        elif ch in ("1", "L", "|"):
            last2[i] = "I"

    letters = "".join(last2)
    if len(letters) != 2 or not letters.isalpha():
        return None

    return digits + letters


