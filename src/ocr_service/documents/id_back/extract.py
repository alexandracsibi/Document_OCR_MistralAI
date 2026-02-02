from __future__ import annotations

from typing import Optional

from ocr_service.core.utils.extract import nextline_value, nextline_value_guarded
from ocr_service.core.utils.ocr_text import search_value
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