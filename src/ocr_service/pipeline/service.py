from __future__ import annotations
from typing import Any
from ocr_service.clients.mistral_ocr import run_ocr_image_path
from ocr_service.core.types import DocType, ExtractionResult, OCRResult
from ocr_service.core.utils.hash import sha256_file
from ocr_service.ocr.cache import load_cached_ocr, save_cached_ocr
from ocr_service.config.settings import get_settings
from ocr_service.documents.registry import get_processor

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
    warnings: list[str] = []

    # OCR with cache
    cache_key = f"{sha256_file(image_path)}::{settings.ocr_model}::{settings.ocr_table_format}"
    raw_cached = None

    if settings.ocr_cache_enabled and not settings.ocr_cache_force_refresh:
        raw_cached = load_cached_ocr(settings.ocr_cache_dir, cache_key)

    if raw_cached is not None:
        ocr = _ocrresult_from_raw(raw_cached)
        ocr_used_cache = True
    else:
        ocr = run_ocr_image_path(
            client=client,
            image_path=image_path,
            model=settings.ocr_model,
            table_format=settings.ocr_table_format,
        )
        ocr_used_cache = False

        if settings.ocr_cache_enabled:
            save_cached_ocr(settings.ocr_cache_dir, cache_key, ocr.raw)

    #Processor dispatch 
    if not ocr.text:
        warnings.append("OCR returned empty text. Check image quality or OCR request format.")

    processor = get_processor(doc_type)
    if processor is None:
        fields: dict[str, Any] = {}
        warnings.append(f"No processor registered for doc_type={doc_type.value}.")
    else:
        fields = processor.extract_fields(ocr)

    if ocr_used_cache:
        warnings.append("OCR loaded from cache.")
    else:
        warnings.append("OCR fetched from Mistral and cached.")

    #TODO Stub scoring (for now)
    confidence = 0.5 if ocr.text else 0.0
    is_correct = False

    # if confidence < settings.confidence_threshold:
    #     warnings.append(f"Confidence below threshold: {confidence:.2f} < {settings.confidence_threshold:.2f}")

    return ExtractionResult(
        doc_type=doc_type,
        is_correct_document=is_correct,
        confidence=confidence,
        fields=fields,
        warnings=warnings,
    )