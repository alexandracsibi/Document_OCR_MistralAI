from __future__ import annotations
from typing import Any, Dict


FIELDS = [
    "document_number",
    "country_code",
    "full_name",
    "birth_name", # optional + not present on all passports 
    "nationality",
    "birth_date",
    "sex",
    "birth_place",
    "issue_date",
    "issuing_authority",
    "expiry_date",
]


def empty() -> Dict[str, Any]:
    """
    Return an empty extraction result for ID front.
    All fields are present and initialized to None.
    """
    return {field: None for field in FIELDS}