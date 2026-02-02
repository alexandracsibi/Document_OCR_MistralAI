from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional


def _sniff_mime(data: bytes) -> Optional[str]:
    # PDF
    if len(data) >= 4 and data[:4] == b"%PDF":
        return "application/pdf"
    # JPEG
    if len(data) >= 3 and data[:3] == b"\xFF\xD8\xFF":
        return "image/jpeg"
    # PNG
    if len(data) >= 8 and data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    # WEBP
    if len(data) >= 12 and data[0:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def file_path_to_data_url(path: str) -> str:
    """
    Supports jpg/png/webp/pdf by sniffing bytes and emitting a proper data URL.
    """
    data = Path(path).read_bytes()
    mime = _sniff_mime(data)
    if not mime:
        raise ValueError("Unsupported file type (expected pdf/jpg/png/webp).")

    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"


# Backward-compatible alias (optional)
def image_path_to_data_url(path: str) -> str:
    return file_path_to_data_url(path)
