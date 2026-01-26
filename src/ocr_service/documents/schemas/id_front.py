from __future__ import annotations
from ocr_service.documents.schemas.common import empty_fields

FIELDS = [
    "document_type",
    "full_name",
    "sex",
    "birth_date",
    "expiry_date",
    "document_number",
    "nationality",
]

def empty() -> dict[str, object]:
    return empty_fields(FIELDS)