from __future__ import annotations
import base64
from pathlib import Path


def image_path_to_data_url(path: str) -> str:
    """
    Current behavior: assumes JPEG.
    TODO: extend later to detect MIME type or accept bytes/png/pdf.
    """
    data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"
