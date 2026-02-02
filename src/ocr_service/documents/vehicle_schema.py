from __future__ import annotations
from typing import Any, Dict

FIELDS = [
    "A","B", "D.1","D.2","D.3","E","F.1","G",
    "H",
    "I","J",
    "K",
    "O",
    "P.1","P.2","P.3","P.5",
    "Q",
    "manufacture_year",
    "gearbox_type",
    "R","S.1","S.2",
    "V.9",
]

def empty() -> Dict[str, Any]:
    return {k: None for k in FIELDS}
