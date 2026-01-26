from __future__ import annotations
from typing import Any, Dict
from ocr_service.core.types import OCRResult
from ocr_service.documents.base import DocumentProcessor
from ocr_service.documents.schemas import id_back
from ocr_service.core.utils.text import (
    split_lines,
    extract_nextline_value,
    extract_nextline_value_guarded,
    extract_inline_value,
)
from ocr_service.core.utils import patterns

class IDBackProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "ID_BACK"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        text = ocr.text or ""
        lines = split_lines(text)

        fields = id_back.empty()

        STOP_LABELS = [
            patterns.BIRTH_PLACE_LABEL,
            patterns.BIRTH_NAME_LABEL,
            patterns.MOTHERS_NAME_LABEL,
            patterns.ORIGIN_PLACE_LABEL,
        ]

        # next-line fields (strict, no fallback guessing)
        fields["birth_place"] = extract_nextline_value(lines, patterns.BIRTH_PLACE_LABEL)
        fields["birth_name"] = extract_nextline_value_guarded(lines, patterns.BIRTH_NAME_LABEL, STOP_LABELS)
        fields["mothers_name"] = extract_nextline_value(lines, patterns.MOTHERS_NAME_LABEL)
        fields["origin_place"] = extract_nextline_value_guarded(lines, patterns.ORIGIN_PLACE_LABEL, STOP_LABELS)

        # inline field
        fields["issuing_authority"] = extract_inline_value(
            text, patterns.ISSUING_AUTHORITY_INLINE
        )

        return {k: fields.get(k) for k in id_back.FIELDS}
