from __future__ import annotations
from typing import Any
from ocr_service.core.types import OCRResult
from ocr_service.core.utils.image import image_path_to_data_url


def run_ocr_image_path(*, client: Any, image_path: str, model: str = "mistral-ocr-latest", table_format: str = "markdown") -> OCRResult:
    """
    Returns concatenated text from pages[].markdown if present.
    """
    data_url = image_path_to_data_url(image_path)

    resp = client.ocr.process(
        model=model,
        document={
            "type": "image_url",
            "image_url": data_url,
        },
        table_format=table_format,
    )

    # Normalize response
    raw = resp if isinstance(resp, dict) else resp.model_dump()

    pages = raw.get("pages", [])
    text_parts: list[str] = []
    for p in pages:
        md = p.get("markdown")
        if isinstance(md, str) and md.strip():
            text_parts.append(md.strip())

    text = "\n\n".join(text_parts).strip()

    return OCRResult(text=text, raw=raw)
