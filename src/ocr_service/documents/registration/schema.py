from __future__ import annotations
from typing import Any, Dict

FIELDS = [
    "document_number",
    "A","B", "D.1","D.2","D.3","E","F.1","G",
    "H", # optional
    "I","J",
    "K", # optional
    "O",  # optional only if vontato horog O.1, O.2 (0-3)
    "P.1","P.2","P.3",
    "P.5", # not present after 2025 april
    "Q", "manufacture_year", "gearbox_type",
    "R","S.1",
    "S.2", # optional only if bike
    "V.9"
]

def empty() -> Dict[str, Any]:
    """
    Return an empty extraction result for ID front.
    All fields are present and initialized to None.
    """
    return {field: None for field in FIELDS}