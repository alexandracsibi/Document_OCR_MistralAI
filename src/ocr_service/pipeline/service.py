from __future__ import annotations
from typing import Any
from ocr_service.clients.mistral_ocr import run_ocr_image_path
from ocr_service.core.types import DocType, ExtractionResult, OCRResult
from ocr_service.config.settings import get_settings
from ocr_service.documents.registry import get_processor

from ocr_service.documents import personal_schema, vehicle_schema

VEHICLE_TYPES = {"REGISTRATION", "COC"}

def unify_payload(doc_type_value: str, fields: dict) -> tuple[str, dict]:
    if doc_type_value in VEHICLE_TYPES:
        out = vehicle_schema.empty()
        for k in vehicle_schema.FIELDS:
            if k in fields:
                out[k] = fields.get(k)
        return "vehicle_data", out

    out = personal_schema.empty()
    for k in personal_schema.FIELDS:
        if k in fields:
            out[k] = fields.get(k)
    return "personal_data", out


def process_document(*, client: Any, doc_type: DocType, image_path: str) -> ExtractionResult:
    """
    - Runs OCR (with local disk caching)
    - Dispatches to doc-type processor (currently stubs)
    - Returns stable JSON wrapper

    TODO -> Extraction logic + correctness scoring will be refined later.
    """
    settings = get_settings()

    ocr = run_ocr_image_path(
        client=client,
        image_path=image_path,
        model=settings.ocr_model,
        table_format=settings.ocr_table_format,
    ) 

    #Processor dispatch 
    processor = get_processor(doc_type)
    if processor is None:
        fields: dict[str, Any] = {}
    else:
        fields = processor.extract_fields(ocr)

    # Move document_number out of fields (if present)
    docno = None
    if isinstance(fields, dict):
        docno = fields.pop("document_number", None)

    #TODO Stub scoring (for now)
    confidence = 0.5 if ocr.text else 0.0
    is_correct = True

    # if confidence < settings.confidence_threshold:

    return ExtractionResult(
        doc_type=doc_type,
        document_number=docno,
        is_correct_document=is_correct,
        confidence=confidence,
        fields=fields,
    )