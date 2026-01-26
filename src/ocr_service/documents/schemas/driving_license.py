from __future__ import annotations
from ocr_service.documents.schemas.common import empty_fields

FIELDS = [
    "full_name",
    "birth_date",
    "birth_place",
    "issue_date",
    "expiry_date",
    "issuing_authority",
    "licence_number",
]

def empty() -> dict[str, object]:
    return empty_fields(FIELDS)