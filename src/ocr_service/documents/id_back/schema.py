from __future__ import annotations
from typing import Any, Dict

FIELDS = [
    "document_number",
    "full_name", # in MRZ format: LASTNAME<<FIRSTNAME<MIDDLENAME
    "birth_date", # MRZ in YYMMDD format
    "birth_place",
    "birth_name", #can be NULL
    "mothers_name",
    "origin_place", # can be NULL
    "issuing_authority",
]

def empty() -> Dict[str, Any]:
    """
    Return an empty extraction result for ID front.
    All fields are present and initialized to None.
    """
    return {field: None for field in FIELDS}