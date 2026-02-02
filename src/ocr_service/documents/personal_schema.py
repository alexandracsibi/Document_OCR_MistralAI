from __future__ import annotations
from typing import Any, Dict

FIELDS = [
    "full_name",

    "birth_date",
    "birth_place",
    "birth_name",

    "sex",
    "nationality",

    "issuing_authority",
    "issue_date",
    "expiry_date",

    "mothers_name",

    "permanent_address",
    "permanent_reporting_time",
    "temporary_address",
    "temporary_reporting_time",
    "temporary_validity",

    "country_code",     # passport only
    "origin_place",     # id_back only
]

def empty() -> Dict[str, Any]:
    return {k: None for k in FIELDS}
