from __future__ import annotations
from typing import Any, Dict

FIELDS = [
    "document_number",
    "full_name",
    "expiry_date",
]

def empty() -> Dict[str, Any]:
    """
    Return an empty extraction result for ID front.
    All fields are present and initialized to None.
    """
    return {field: None for field in FIELDS}