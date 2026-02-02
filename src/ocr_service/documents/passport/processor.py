from __future__ import annotations

from typing import Any, Dict

from ocr_service.core.types import OCRResult
from ocr_service.documents.base import DocumentProcessor
from ocr_service.core.utils.extract import norm_lines
from ocr_service.documents.passport import schema, extract


class PassportProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "PASSPORT"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        text = ocr.text or ""
        lines = norm_lines(text)
        fields = schema.empty()

        fields["country_code"] = extract.extract_country_code(lines)
        fields["document_number"] = extract.extract_document_number(lines)

        fields["full_name"] = extract.extract_full_name(lines)
        fields["birth_name"] = extract.extract_birth_name(lines)

        fields["nationality"] = extract.extract_nationality(lines)
        fields["birth_date"] = extract.extract_birth_date(text)
        fields["sex"] = extract.extract_sex(lines)
        fields["birth_place"] = extract.extract_birth_place(lines)

        fields["issue_date"] = extract.extract_issue_date(text)
        fields["issuing_authority"] = extract.extract_issuing_authority(lines)
        fields["expiry_date"] = extract.extract_expiry_date(text)

        return {k: fields.get(k) for k in schema.FIELDS}
