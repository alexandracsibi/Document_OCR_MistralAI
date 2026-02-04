from __future__ import annotations

from typing import Any, Dict

from ocr_service.core.types import OCRResult
from ocr_service.documents.base import DocumentProcessor
from ocr_service.documents.registration import schema, postprocess as pp
from ocr_service.documents.registration import extract as ex


class RegistrationProcessor(DocumentProcessor):
    @property
    def doc_type(self) -> str:
        return "REGISTRATION"

    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        text = ocr.text or ""
        fields = schema.empty()

        fields["document_number"] = ex.extract_document_number(text)
        fields["A"] = ex.extract_A(text)
        fields["B"] = ex.extract_B(text)

        fields["D.1"] = ex.extract_D1(text)
        fields["D.2"] = ex.extract_D2(text)
        fields["D.3"] = ex.extract_D3(text)

        fields["E"] = ex.extract_E(text)

        # Mass / limits
        fields["F.1"] = ex.extract_F1(text)
        fields["G"] = ex.extract_G(text)

        # Optional / misc
        fields["H"] = ex.extract_H(text)
        fields["I"] = ex.extract_I(text)
        fields["J"] = ex.extract_J(text)
        fields["K"] = ex.extract_K(text)
        fields["O"] = ex.extract_O(text)

        # Engine / fuel
        fields["P.1"] = ex.extract_P1(text)
        fields["P.2"] = ex.extract_P2(text)
        fields["P.3"] = ex.extract_P3(text)
        fields["P.5"] = ex.extract_P5(text)

        # Optional bike-only
        fields["Q"] = ex.extract_Q(text)

        # Color
        fields["R"] = ex.extract_R(text)

        # Seats
        fields["S.1"] = ex.extract_S1(text)
        fields["S.2"] = ex.extract_S2(text)

        # Emissions/class
        fields["V.9"] = ex.extract_V9(text)

        # HU textual
        fields["manufacture_year"] = ex.extract_manufacture_year(text)
        fields["gearbox_type"] = ex.extract_gearbox_type(text)

        fields = pp.postprocess(fields)

        return {k: fields.get(k) for k in schema.FIELDS}