from __future__ import annotations
from ocr_service.documents.schemas.common import empty_fields

FIELDS = [
    "brith_name",
    "birth_place",
    "birth_date",
    "sex",
    "nationality",
    "mothers_name",
    "issuing_authority",
]

def empty() -> dict[str, object]:
    return empty_fields(FIELDS)