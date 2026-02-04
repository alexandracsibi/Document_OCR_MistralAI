from __future__ import annotations

from typing import Any, Optional
from ocr_service.documents.registration import rules as rr
from ocr_service.core.utils.normalize import empty_to_none, norm_ws

_DOCNO_PREFIX_FIX = str.maketrans({
    "0": "O",
    "1": "I",  # could be I/J; choose I as canonical
})

_DOCNO_DIGIT_FIX = str.maketrans({
    "O": "0",
    "I": "1",
    "J": "1",
    # keep digits as-is
})

_VIN_FIX = str.maketrans({
    "I": "1",
    "O": "0",
    "Q": "0",
})

def normalize_document_number(raw: Optional[str]) -> Optional[str]:
    """
    Canonicalize registration doc number (2 letters + 5 digits) with OCR fixes.

    Input is tolerant (rules.DOCUMENT_NUMBER_VALUE allows [A-Z10]{2} + [0-9OIJ]{5}).
    Output is strict: 2 A-Z letters + 5 digits (no OCR-confusable chars remain).
    """
    s = norm_ws(raw)
    if not s:
        return None

    m = rr.DOCUMENT_NUMBER_VALUE.search(s)
    if not m:
        return None

    prefix_raw = (m.group(1) or "").upper()
    digits_raw = (m.group(2) or "").upper()

    prefix = prefix_raw.translate(_DOCNO_PREFIX_FIX)
    digits = digits_raw.translate(_DOCNO_DIGIT_FIX)

    if len(prefix) != 2 or not prefix.isalpha():
        return None
    if len(digits) != 5 or not digits.isdigit():
        return None

    return f"{prefix}{digits}"


def normalize_vin(raw: Optional[str]) -> Optional[str]:
    """
    VIN canonicalization:
    - take first 17-char token matched by VIN_VALUE
    - map OCR I/O/Q -> 1/0/0
    - validate final VIN has length 17, alnum only, and contains no I/O/Q
    """
    s = norm_ws(raw)
    if not s:
        return None

    m = rr.VIN_VALUE.search(s)
    if not m:
        return None

    vin = (m.group(1) if m.lastindex else m.group(0)) or ""
    vin = "".join(vin.split()).upper()
    if len(vin) != 17:
        return None

    vin = vin.translate(_VIN_FIX)

    if len(vin) != 17 or not vin.isalnum():
        return None
    if any(ch in vin for ch in ("I", "O", "Q")):
        return None

    return vin


def postprocess(fields: dict[str, Any]) -> dict[str, Any]:
    """
    - Whitespace-normalize all string field values (empty -> None)
    - Normalize VIN (E) inside fields
    - Normalize document_number outside fields
    """
    out = dict(fields or {})

    for k, v in list(out.items()):
        out[k] = empty_to_none(v)

    # VIN is field E in registration
    out["E"] = normalize_vin(out.get("E"))

    out["document_number"] = normalize_document_number(out.get("document_number"))

    return out