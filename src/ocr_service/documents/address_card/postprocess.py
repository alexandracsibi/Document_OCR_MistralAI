from __future__ import annotations

from typing import Any, Optional, Tuple

from ocr_service.core.utils.normalize import norm_ws, empty_to_none
from ocr_service.documents.address_card import rules as rr

# ---------------------------
# Address-card specific cleanup
# ---------------------------

_DIGIT_FIX = str.maketrans({
    "O": "0",
    "I": "1",
    "J": "1",
    "L": "1",
    "l": "1",  # in case something slips through before upper()
})

_LETTER_FIX = str.maketrans({
    "0": "O",
    "1": "I",
})

def _normalize_document_number(raw: Optional[str]) -> Optional[str]:
    """
    Canonical format: 'dddddd XX' (upper, single space).

    - First part (6 digits): applies OCR fixes O->0, I/J/L->1
    - Second part (2 letters): applies OCR fixes 0->O, 1->I
    - Then strict-validate as: 6 digits + space + 2 letters
    """
    s = norm_ws(raw)
    if not s:
        return None

    m = rr.DOCNO_VALUE.search(s)  # tolerant match anywhere
    if not m:
        return None

    digits_raw = (m.group(1) or "").strip()
    letters_raw = (m.group(2) or "").strip()

    # zone-aware OCR correction
    digits = digits_raw.upper().translate(_DIGIT_FIX)
    letters = letters_raw.upper().translate(_LETTER_FIX)

    cand = f"{digits} {letters}"

    # strict canonical validation (NO tolerant chars allowed anymore)
    if not rr.DOCNO_CANON.fullmatch(cand):
        return None

    return cand

def postprocess(fields: dict[str, Any]) -> dict[str, Any]:
    out = dict(fields or {})

    # 0) normalize strings + empty -> None
    for k, v in list(out.items()):
        out[k] = empty_to_none(v)
    
    # 1) canonicalize docno (and drop if not strictly valid)
    out["document_number"] = _normalize_document_number(out.get("document_number"))

    # 2) Külföldi cím -> permanent_reporting_time must be null
    if rr.FOREIGN_ADDRESS_VALUE.fullmatch(out.get("permanent_address") or ""):
        out["permanent_reporting_time"] = None

    # 3) reporting_time < validity for temporary address
    temp_addr = out.get("temporary_address")
    temp_rpt = out.get("temporary_reporting_time")
    temp_val = out.get("temporary_validity")
    if temp_addr:
        # Only validate ordering if BOTH dates are present
        if temp_rpt is not None and temp_val is not None:
            if not (temp_rpt < temp_val):
                out["temporary_reporting_time"] = None
                out["temporary_validity"] = None

    # 4) If Külföldi cím then birth_place must NOT contain Magyarország
    if rr.FOREIGN_ADDRESS_VALUE.fullmatch(out.get("permanent_address") or ""):
        bp = out.get("birth_place") or ""
        if rr.HUNGARY_WORD.search(bp):
            out["birth_place"] = None

    return out
