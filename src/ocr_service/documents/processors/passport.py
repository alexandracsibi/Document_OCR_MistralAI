from __future__ import annotations
from typing import Any, Dict
from ocr_service.core.types import OCRResult
from ocr_service.documents.base import DocumentProcessor
from ocr_service.documents.schemas import passport

class PassportProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "PASSPORT"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        return passport.empty()
