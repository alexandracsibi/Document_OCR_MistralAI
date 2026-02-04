from __future__ import annotations

from typing import Any, Dict

from ocr_service.core.types import OCRResult
from ocr_service.documents.base import DocumentProcessor
from ocr_service.core.utils.extract import norm_lines
from ocr_service.documents.address_card import schema, extract as ex, postprocess as pp


class AddressCardProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "ADDRESS_CARD"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        text = ocr.text or ""
        lines = norm_lines(text)

        fields = schema.empty()

        fields["document_number"] = ex.extract_document_number(lines, text)
        fields["full_name"] = ex.extract_full_name(lines)

        birth_place, birth_date = ex.extract_birth_place_and_date(lines)
        fields["birth_place"] = birth_place
        fields["birth_date"] = birth_date

        fields["mothers_name"] = ex.extract_mothers_name(lines)

        fields["permanent_address"] = ex.extract_permanent_address(lines)
        fields["permanent_reporting_time"] = ex.extract_permanent_reporting_time(lines)

        fields["temporary_address"] = ex.extract_temporary_address(lines)
        fields["temporary_reporting_time"] = ex.extract_temporary_reporting_time(lines)
        fields["temporary_validity"] = ex.extract_temporary_validity(lines)

        issuing_authority, issue_date = ex.extract_issuing_authority_and_issue_date(lines)
        fields["issuing_authority"] = issuing_authority
        fields["issue_date"] = issue_date

        fields = pp.postprocess(fields)
        
        return {k: fields.get(k) for k in schema.FIELDS}
