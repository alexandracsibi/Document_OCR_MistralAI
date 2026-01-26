from __future__ import annotations
from ocr_service.documents.schemas.common import empty_fields

FIELDS = [
    "A","B","C.1.1","C.1.2","C.1.3","D.1","D.2","D.3","E","F.1","G",
    "H", # optional
    "I","J",
    "K", # optional
    "O", # optional only if vontato horog
    "P.1","P.2","P.3",
    "P.5", # not present after 2025 april
    "Q", "manufacture_year", "gearbox_type",
    "R","S.1",
    "S.2", # optional only if bike
    "V.9"
]
def empty() -> dict[str, object]:
    return empty_fields(FIELDS)