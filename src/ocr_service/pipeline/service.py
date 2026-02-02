from __future__ import annotations
from typing import Any
from ocr_service.clients.mistral_ocr import run_ocr_image_path
from ocr_service.core.types import DocType, ExtractionResult, OCRResult
from ocr_service.core.utils.hash import sha256_file
from ocr_service.ocr.cache import load_cached_ocr, save_cached_ocr
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

def _ocrresult_from_raw(raw: dict[str, Any]) -> OCRResult:
    pages = raw.get("pages", [])
    parts: list[str] = []
    for p in pages:
        md = p.get("markdown")
        if isinstance(md, str) and md.strip():
            parts.append(md.strip())
    text = "\n\n".join(parts).strip()
    return OCRResult(text=text, raw=raw)

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

    # OCR with cache
    # cache_key = f"{sha256_file(image_path)}::{settings.ocr_model}::{settings.ocr_table_format}"
    # raw_cached = None

    # if settings.ocr_cache_enabled and not settings.ocr_cache_force_refresh:
    #     raw_cached = load_cached_ocr(settings.ocr_cache_dir, cache_key)

    # if raw_cached is not None:
    #     ocr = _ocrresult_from_raw(raw_cached)

    # else:
    #     ocr = run_ocr_image_path(
    #         client=client,
    #         image_path=image_path,
    #         model=settings.ocr_model,
    #         table_format=settings.ocr_table_format,
    #     )

    #     if settings.ocr_cache_enabled:
    #         save_cached_ocr(settings.ocr_cache_dir, cache_key, ocr.raw)

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
    is_correct = False

    # if confidence < settings.confidence_threshold:

    return ExtractionResult(
        doc_type=doc_type,
        document_number=docno,
        is_correct_document=is_correct,
        confidence=confidence,
        fields=fields,
    )