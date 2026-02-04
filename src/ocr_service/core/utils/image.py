from __future__ import annotations

import base64
from pathlib import Path

_MIME_BY_EXT = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".pdf": "application/pdf",
}

def image_path_to_data_url(path: str) -> str:
    p = Path(path)
    data = p.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")

    mime = _MIME_BY_EXT.get(p.suffix.lower())
    if not mime:
        # fallback (still works for many cases, but better to pass correct ext)
        mime = "application/octet-stream"

    return f"data:{mime};base64,{b64}"
