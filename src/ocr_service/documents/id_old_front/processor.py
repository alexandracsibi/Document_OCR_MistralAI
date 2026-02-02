from __future__ import annotations

from typing import Any, Dict

from ocr_service.core.types import OCRResult
from ocr_service.documents.base import DocumentProcessor
from ocr_service.documents.id_old_front import schema, extract


class IDOldFrontProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "ID_OLD_FRONT"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        text = ocr.text or ""
        fields = schema.empty()

        fields["full_name"] = extract.extract_full_name(text)
        fields["expiry_date"] = extract.extract_expiry_date(text)
        fields["document_number"] = extract.extract_document_number(text)

        return {k: fields.get(k) for k in schema.FIELDS}
