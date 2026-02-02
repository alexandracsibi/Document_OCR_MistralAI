from __future__ import annotations

from typing import Any, Dict

from ocr_service.core.types import OCRResult
from ocr_service.documents.base import DocumentProcessor
from ocr_service.documents.driving_license import schema
from ocr_service.documents.driving_license import extract as ex


class DrivingLicenseProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "DRIVING_LICENSE"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        text = ocr.text or ""

        fields = schema.empty()

        kv = ex.collect_kv(text)

        fields["full_name"] = ex.extract_full_name(kv)

        birth_date, birth_place = ex.extract_birth_date_and_place(kv)
        fields["birth_date"] = birth_date
        fields["birth_place"] = birth_place

        fields["issue_date"] = ex.extract_issue_date(kv)
        fields["expiry_date"] = ex.extract_expiry_date(kv)

        fields["issuing_authority"] = ex.extract_issuing_authority(kv)
        fields["document_number"] = ex.extract_licence_number(kv)

        return {k: fields.get(k) for k in schema.FIELDS}
