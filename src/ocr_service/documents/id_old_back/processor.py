from __future__ import annotations

from typing import Any, Dict

from ocr_service.core.types import OCRResult
from ocr_service.documents.base import DocumentProcessor
from ocr_service.documents.id_old_back import schema, extract


class IDOldBackProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "ID_OLD_BACK"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        text = ocr.text or ""
        fields = schema.empty()

        fields["birth_name"] = extract.extract_birth_name(text)  
        fields["birth_place"] = extract.extract_birth_place(text)
        fields["birth_date"] = extract.extract_birth_date(text)
        fields["sex"] = extract.extract_sex(text)
        fields["nationality"] = extract.extract_nationality(text)
        fields["mothers_name"] = extract.extract_mothers_name(text)
        fields["issuing_authority"] = extract.extract_issuing_authority(text)

        return {k: fields.get(k) for k in schema.FIELDS}
