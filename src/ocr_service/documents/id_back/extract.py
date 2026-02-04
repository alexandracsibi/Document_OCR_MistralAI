from __future__ import annotations

import re
from typing import Optional, List

from ocr_service.core.utils.extract import nextline_value, nextline_value_guarded, fallback_value
from ocr_service.core.utils.ocr_text import mrz_check_digit, parse_mrz_birth_date_yyMMdd, search_value, find_mrz_td1_block
from ocr_service.core.utils.normalize import normalize_id_number
from ocr_service.documents.id_back import rules as rr


def extract_birth_place(lines: list[str]) -> Optional[str]:
    return nextline_value(lines, rr.BIRTH_PLACE_LABEL)


def extract_birth_name(lines: list[str]) -> Optional[str]:
    res = nextline_value_guarded(lines, rr.BIRTH_NAME_LABEL, rr.STOP_LABELS)
    return res.value  # None if missing/empty OR blocked by stop label


def extract_mothers_name(lines: list[str]) -> Optional[str]:
    return nextline_value(lines, rr.MOTHERS_NAME_LABEL)


def extract_origin_place(lines: list[str]) -> Optional[str]:
    res = nextline_value_guarded(lines, rr.ORIGIN_PLACE_LABEL, rr.STOP_LABELS)
    return res.value


def extract_issuing_authority(text: str) -> Optional[str]:
    return search_value(text, rr.ISSUING_AUTHORITY_INLINE)

def extract_document_number(text: str, lines: List[str]) -> Optional[str]:
    """
    Prefer MRZ doc number (TD1 line1 pos 6-14) then fallback to global candidate regex.
    Returns canonical: 6 digits + 2 letters (no space).
    """
    mrz = find_mrz_td1_block(lines)
    if mrz:
        l1, _, _ = mrz
        # TD1 line1: positions 6-14 (1-indexed) => slice [5:14], 9 chars total
        docno_field = l1[5:14]           # 9 chars (may include '<' padding)
        docno_core = docno_field.replace("<", "")
        if len(docno_core) >= 8:
            norm = normalize_id_number(docno_core[:8])
            if norm:
                return norm

    # fallback: global search (may hit MRZ or noise; normalization filters hard)
    raw = fallback_value(text, rr.ID_NUMBER_CANDIDATE)
    if raw:
        return normalize_id_number(raw)
    return None

def extract_full_name(lines: List[str]) -> Optional[str]:
    """
    Extract from MRZ line3: SURNAME<<GIVEN<NAMES
    Returns a whitespace-collapsed full name in uppercase.
    """
    mrz = find_mrz_td1_block(lines)
    if not mrz:
        return None
    _, _, l3 = mrz

    s = l3.strip("<")
    if not s:
        return None

    parts = s.split("<<", 1)
    surname = parts[0].replace("<", " ").strip()
    given = parts[1].replace("<", " ").strip() if len(parts) > 1 else ""
    full = " ".join([surname, given]).strip()
    full = " ".join(full.split())
    return full or None

def extract_birth_date(lines: List[str]) -> Optional[str]:
    """
    Extract DOB from MRZ line2 pos 1-6 (YYMMDD) and return ISO YYYY-MM-DD.
    """
    mrz = find_mrz_td1_block(lines)
    if not mrz:
        return None
    _, l2, _ = mrz

    dob = l2[0:6]
    dob_cd = l2[6:7]

    # optional: require check digit to match when present
    if re.fullmatch(r"\d{6}", dob) and dob_cd.isdigit():
        if mrz_check_digit(dob) != dob_cd:
            return None

    return parse_mrz_birth_date_yyMMdd(dob)