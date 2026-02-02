from __future__ import annotations
from typing import Any

from ocr_service.core.types import OCRResult
from ocr_service.core.utils.image import file_path_to_data_url


def _guess_document_type_from_data_url(data_url: str) -> str:
    # data:<mime>;base64,...
    # If it's pdf => document_url, else image_url
    if data_url.startswith("data:application/pdf"):
        return "document_url"
    return "image_url"


def run_ocr_image_path(*, client: Any, image_path: str, model: str = "mistral-ocr-latest", table_format: str = "markdown") -> OCRResult:
    data_url = file_path_to_data_url(image_path)
    doc_type = _guess_document_type_from_data_url(data_url)

    payload_key = "document_url" if doc_type == "document_url" else "image_url"

    resp = client.ocr.process(
        model=model,
        document={
            "type": doc_type,
            payload_key: data_url,
        },
        table_format=table_format,
    )

    raw = resp if isinstance(resp, dict) else resp.model_dump()

    pages = raw.get("pages", [])
    text_parts: list[str] = []
    for p in pages:
        md = p.get("markdown")
        if isinstance(md, str) and md.strip():
            text_parts.append(md.strip())

    text = "\n\n".join(text_parts).strip()
    return OCRResult(text=text, raw=raw)
