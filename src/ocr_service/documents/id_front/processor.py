from __future__ import annotations
from typing import Any, Dict, Optional

from ocr_service.core.types import OCRResult
from ocr_service.documents.base import DocumentProcessor
from ocr_service.documents.id_front import schema
from ocr_service.documents.id_front import extract as ex

class IDFrontProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "ID_FRONT"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        text = ocr.text or ""
        fields = schema.empty()

        fields["full_name"] = ex.extract_full_name(text)
        fields["sex"] = ex.extract_sex(text)
        fields["nationality"] = ex.extract_nationality(text)

        birth_iso, expiry_iso = ex.extract_birth_and_expiry_dates(text)
        fields["birth_date"] = birth_iso
        fields["expiry_date"] = expiry_iso

        fields["document_number"] = ex.extract_document_number(
            text,
            birth_iso=birth_iso,
            expiry_iso=expiry_iso,
        )

        return {k: fields.get(k) for k in schema.FIELDS}