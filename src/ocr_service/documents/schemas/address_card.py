from __future__ import annotations
from ocr_service.documents.schemas.common import empty_fields

FIELDS = [
    "full_name",
    "birth_date",
    "birth_place",
    "mothers_name",
    "permanent_address",
    "temporary_address", # optional
    "issuing_authority",
    "validity", # if temporary address is present
    "reporting_time",
]

def empty() -> dict[str, object]:
    return empty_fields(FIELDS)