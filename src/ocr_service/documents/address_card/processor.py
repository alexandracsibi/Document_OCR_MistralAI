from __future__ import annotations

from typing import Any, Dict

from ocr_service.core.types import OCRResult
from ocr_service.documents.base import DocumentProcessor
from ocr_service.core.utils.extract import norm_lines
from ocr_service.documents.address_card import schema, extract


class AddressCardProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "ADDRESS_CARD"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        text = ocr.text or ""
        lines = norm_lines(text)

        fields = schema.empty()

        fields["document_number"] = extract.extract_document_number(lines, text)
        fields["full_name"] = extract.extract_full_name(lines)

        birth_place, birth_date = extract.extract_birth_place_and_date(lines)
        fields["birth_place"] = birth_place
        fields["birth_date"] = birth_date

        fields["mothers_name"] = extract.extract_mothers_name(lines)

        fields["permanent_address"] = extract.extract_permanent_address(lines)
        fields["permanent_reporting_time"] = extract.extract_permanent_reporting_time(lines)

        fields["temporary_address"] = extract.extract_temporary_address(lines)
        fields["temporary_reporting_time"] = extract.extract_temporary_reporting_time(lines)
        fields["temporary_validity"] = extract.extract_temporary_validity(lines)

        issuing_authority, issue_date = extract.extract_issuing_authority_and_issue_date(lines)
        fields["issuing_authority"] = issuing_authority
        fields["issue_date"] = issue_date
        
        return {k: fields.get(k) for k in schema.FIELDS}
