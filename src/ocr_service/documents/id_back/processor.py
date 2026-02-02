from __future__ import annotations

from typing import Any, Dict

from ocr_service.core.types import OCRResult
from ocr_service.documents.base import DocumentProcessor
from ocr_service.core.utils.extract import norm_lines
from ocr_service.documents.id_back import schema
from ocr_service.documents.id_back import extract as ex


class IDBackProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "ID_BACK"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        text = ocr.text or ""
        lines = norm_lines(text)
        fields = schema.empty()

        fields["birth_place"] = ex.extract_birth_place(lines)
        fields["birth_name"] = ex.extract_birth_name(lines)
        fields["mothers_name"] = ex.extract_mothers_name(lines)
        fields["origin_place"] = ex.extract_origin_place(lines)
        fields["issuing_authority"] = ex.extract_issuing_authority(text)

        return {k: fields.get(k) for k in schema.FIELDS}
