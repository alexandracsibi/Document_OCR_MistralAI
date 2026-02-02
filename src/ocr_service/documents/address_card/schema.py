from __future__ import annotations
from typing import Any, Dict

FIELDS = [
    "document_number",
    "full_name",
    "birth_date",
    "birth_place",
    "mothers_name",
    "permanent_address",
    "permanent_reporting_time", # can be null if "kulfoldi cim"
    "temporary_address", # optional
    "temporary_reporting_time", # optional
    "temporary_validity",   # optional
    "issuing_authority",
    "issue_date", 
]

def empty() -> Dict[str, Any]:
    """
    Return an empty extraction result for ID front.
    All fields are present and initialized to None.
    """
    return {field: None for field in FIELDS}