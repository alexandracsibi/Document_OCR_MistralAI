from __future__ import annotations
from ocr_service.documents.schemas.common import empty_fields

FIELDS = [
    "full_name",
    "expiry_date",
    "document_number",
]

def empty() -> dict[str, object]:
    return empty_fields(FIELDS)