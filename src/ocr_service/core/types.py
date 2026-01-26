from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any


class DocType(str, Enum):
    ID_FRONT = "ID_FRONT"
    ID_BACK = "ID_BACK"
    ID_OLD_FRONT = "ID_OLD_FRONT"
    ID_OLD_BACK = "ID_OLD_BACK"
    DRIVING_LICENSE = "DRIVING_LICENSE"
    ADDRESS_CARD = "ADDRESS_CARD"
    PASSPORT = "PASSPORT"
    REGISTRATION = "REGISTRATION"
    COC = "COC"


@dataclass(frozen=True)
class OCRResult:
    text: str
    raw: dict[str, Any]  # internal only; NOT exposed in final JSON


@dataclass
class ExtractionResult:
    doc_type: DocType
    is_correct_document: bool
    confidence: float
    fields: dict[str, Any]
    warnings: list[str]
