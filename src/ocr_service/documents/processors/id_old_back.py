from __future__ import annotations
from typing import Any, Dict
from ocr_service.core.types import OCRResult
from ocr_service.documents.base import DocumentProcessor
from ocr_service.documents.schemas import id_old_back

class IDOldBackProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "ID_OLD_BACK"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        return id_old_back.empty()
