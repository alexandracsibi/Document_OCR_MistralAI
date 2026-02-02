from __future__ import annotations

import base64
import binascii
import os
import tempfile
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ocr_service.config.mistral_client import get_mistral_client
from ocr_service.core.types import DocType
from ocr_service.pipeline.service import process_document, unify_payload

router = APIRouter()

# Size limits (decoded bytes)
MAX_IMAGE_BYTES = int(os.getenv("API_MAX_IMAGE_BYTES", "6000000"))   # 6 MB
MAX_PDF_BYTES = int(os.getenv("API_MAX_PDF_BYTES", "20000000"))      # 20 MB
ABSOLUTE_MAX_BYTES = int(os.getenv("API_ABSOLUTE_MAX_BYTES", "25000000"))  # 25 MB hard cap

ALLOWED_EXT = {"jpg", "jpeg", "png", "webp", "pdf"}
VEHICLE_TYPES = {"REGISTRATION", "COC"}  # doc_type.value strings


class ProcessRequest(BaseModel):
    doc_type: DocType
    image_base64: str = Field(..., min_length=16)
    extension: Optional[str] = None  # "jpg" / "png" / "pdf" / ...


def _strip_data_url(s: str) -> str:
    s = (s or "").strip()
    if s.startswith("data:"):
        # data:<mime>;base64,AAAA...
        comma = s.find(",")
        if comma != -1:
            return s[comma + 1 :].strip()
    return s


def _sniff_ext(blob: bytes) -> Optional[str]:
    if len(blob) >= 4 and blob[:4] == b"%PDF":
        return "pdf"
    if len(blob) >= 3 and blob[0:3] == b"\xFF\xD8\xFF":
        return "jpg"
    if len(blob) >= 8 and blob[0:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if len(blob) >= 12 and blob[0:4] == b"RIFF" and blob[8:12] == b"WEBP":
        return "webp"
    return None


def _decode_base64_blob(b64: str) -> bytes:
    raw = _strip_data_url(b64)
    try:
        data = base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="Invalid base64 payload.")
    if not data:
        raise HTTPException(status_code=400, detail="Decoded file is empty.")
    if len(data) > ABSOLUTE_MAX_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Payload too large. Max decoded bytes = {ABSOLUTE_MAX_BYTES}.",
        )
    return data


def _choose_ext(req_ext: Optional[str], blob: bytes) -> str:
    if req_ext:
        ext = req_ext.strip().lower().lstrip(".")
        if ext == "jpeg":
            ext = "jpg"
        if ext not in ALLOWED_EXT:
            raise HTTPException(status_code=400, detail=f"Unsupported extension: {req_ext}.")
        return ext

    sniffed = _sniff_ext(blob)
    if not sniffed:
        raise HTTPException(status_code=400, detail="Could not detect file type (pdf/jpg/png/webp only).")
    return sniffed


def _enforce_type_size(blob: bytes, ext: str) -> None:
    max_bytes = MAX_PDF_BYTES if ext == "pdf" else MAX_IMAGE_BYTES
    if len(blob) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File too large for {ext}. Max decoded bytes = {max_bytes}.",
        )


def _write_temp_file(blob: bytes, ext: str) -> str:
    name = f"ocr_{uuid.uuid4().hex}.{ext}"
    path = os.path.join(tempfile.gettempdir(), name)
    with open(path, "wb") as f:
        f.write(blob)
    return path


@router.post("/process")
def process(req: ProcessRequest) -> dict:
    blob = _decode_base64_blob(req.image_base64)
    ext = _choose_ext(req.extension, blob)
    _enforce_type_size(blob, ext)

    path = _write_temp_file(blob, ext)

    try:
        client = get_mistral_client()
        res = process_document(client=client, doc_type=req.doc_type, image_path=path)
        doc_type = res.doc_type.value
        fields = dict(res.fields or {})         # sparse raw fields from processor
        data_key, data = unify_payload(doc_type, fields)  # MUST fill missing keys with None

        return {
            "doc_type": doc_type,
            "document_number": res.document_number,
            "is_correct_document": res.is_correct_document,
            "confidence": round(res.confidence, 4),
            data_key: data,                      # unified (all keys present)
        }
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
