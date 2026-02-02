from __future__ import annotations
from typing import Any, Dict


FIELDS = [
    "birth_name",
    "birth_place",
    "birth_date",
    "sex",
    "nationality",
    "mothers_name",
    "issuing_authority",
]

def empty() -> Dict[str, Any]:
    """
    Return an empty extraction result for ID front.
    All fields are present and initialized to None.
    """
    return {field: None for field in FIELDS}
