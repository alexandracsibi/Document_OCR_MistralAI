from __future__ import annotations
from ocr_service.documents.schemas.common import empty_fields

FIELDS = [
    "birth_place",
    "birth_name", #can be NULL
    "mothers_name",
    "origin_place", # can be NULL
    "issuing_authority",
]

def empty() -> dict[str, object]:
    return empty_fields(FIELDS)
