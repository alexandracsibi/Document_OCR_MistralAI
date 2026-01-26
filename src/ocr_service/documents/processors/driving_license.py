from __future__ import annotations
from typing import Any, Dict
from ocr_service.core.types import OCRResult
from ocr_service.documents.base import DocumentProcessor
from ocr_service.documents.schemas import driving_license
from ocr_service.core.utils.text import (
    split_lines,
    extract_nextline_value,
    extract_nextline_value_guarded,
)
from ocr_service.core.utils import patterns

class DrivingLicenseProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "DRIVING_LICENSE"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        text = ocr.text or ""
        lines = split_lines(text)

        fields = driving_license.empty()


        return {k: fields.get(k) for k in driving_license.FIELDS}
