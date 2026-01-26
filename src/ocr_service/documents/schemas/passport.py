from __future__ import annotations
from ocr_service.documents.schemas.common import empty_fields

FIELDS = [
    "full_name",
    "type",
    "code",
    "pssport_number",
    "nationality",
    "birth_date",
    "birth_place",
    "sex",
    "issue_date",
    "expiry_date",
    "issuing_authority",
]

def empty() -> dict[str, object]:
    return empty_fields(FIELDS)