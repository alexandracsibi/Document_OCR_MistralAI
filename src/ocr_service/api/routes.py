from __future__ import annotations

import base64
import binascii
import os
import tempfile
import uuid
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ocr_service.api.models import ProcessRequest, ProcessResponse
from ocr_service.config.mistral_client import get_mistral_client
from ocr_service.core.types import DocType
from ocr_service.pipeline.service import process_document, unify_payload

router = APIRouter()

# Size limits (bytes)
MAX_IMAGE_BYTES = int(os.getenv("API_MAX_IMAGE_BYTES", "6000000"))   # 6 MB
MAX_PDF_BYTES = int(os.getenv("API_MAX_PDF_BYTES", "20000000"))      # 20 MB
ALLOWED_EXT = {"jpg", "jpeg", "png", "webp", "pdf"}
CHUNK_SIZE = 1024 * 1024  # 1 MB


def _strip_data_url(s: str) -> str:
    s = (s or "").strip()
    if s.startswith("data:"):
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


def _normalize_ext(ext: str) -> str:
    e = (ext or "").strip().lower().lstrip(".")
    return "jpg" if e == "jpeg" else e


def _choose_ext(
    req_ext: Optional[str],
    blob: Optional[bytes],
    filename: Optional[str],
    content_type: Optional[str],
) -> str:
    # 1) explicit extension wins
    if req_ext:
        ext = _normalize_ext(req_ext)
        if ext not in ALLOWED_EXT:
            raise HTTPException(status_code=400, detail=f"Unsupported extension: {req_ext}")
        return ext

    # 2) content-type
    ct = (content_type or "").lower().strip()
    if ct == "application/pdf":
        return "pdf"
    if ct in ("image/jpeg", "image/jpg"):
        return "jpg"
    if ct == "image/png":
        return "png"
    if ct == "image/webp":
        return "webp"

    # 3) filename suffix
    if filename and "." in filename:
        ext = _normalize_ext(filename.rsplit(".", 1)[-1])
        if ext in ALLOWED_EXT:
            return ext

    # 4) sniff (needs bytes)
    if blob:
        sniffed = _sniff_ext(blob)
        if sniffed:
            return sniffed

    raise HTTPException(
        status_code=400,
        detail="Could not determine file type. Provide extension or upload a valid jpg/png/webp/pdf.",
    )


def _max_bytes_for_ext(ext: str) -> int:
    return MAX_PDF_BYTES if ext == "pdf" else MAX_IMAGE_BYTES


def _write_temp_bytes(blob: bytes, ext: str) -> str:
    name = f"ocr_{uuid.uuid4().hex}.{ext}"
    path = os.path.join(tempfile.gettempdir(), name)
    with open(path, "wb") as f:
        f.write(blob)
    return path


async def _save_upload_to_temp(file: UploadFile, ext: str) -> str:
    limit = _max_bytes_for_ext(ext)
    name = f"ocr_{uuid.uuid4().hex}.{ext}"
    path = os.path.join(tempfile.gettempdir(), name)

    total = 0
    try:
        with open(path, "wb") as out:
            while True:
                chunk = await file.read(CHUNK_SIZE)
                if not chunk:
                    break
                total += len(chunk)
                if total > limit:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Max bytes for .{ext} = {limit}.",
                    )
                out.write(chunk)

        if total == 0:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        return path

    except HTTPException:
        try:
            os.remove(path)
        except OSError:
            pass
        raise


def _build_response(res, uid: str) -> dict:
    doc_type = res.doc_type.value
    fields = dict(res.fields or {})
    docno = res.document_number

    data_key, data = unify_payload(doc_type, fields)

    return {
        "uid": uid,
        "doc_type": doc_type,
        "document_number": docno,
        "is_correct_document": res.is_correct_document,
        "confidence": round(res.confidence, 4),
        data_key: data,
    }


# -------------------------
# PRIMARY: multipart/form-data
# -------------------------
@router.post("/process", response_model=ProcessResponse)
async def process_multipart(
    uid: str = Form(...),
    doc_type: DocType = Form(...),
    file: UploadFile = File(...),
) -> dict:
    uid = (uid or "").strip()
    if not uid:
        raise HTTPException(status_code=422, detail="uid must not be empty.")

    # sniff prefix without loading whole file into RAM
    prefix = await file.read(64)
    await file.seek(0)

    ext = _choose_ext(
        req_ext=None,
        blob=prefix,
        filename=file.filename,
        content_type=file.content_type,
    )

    tmp_path = await _save_upload_to_temp(file, ext)
    try:
        client = get_mistral_client()
        res = process_document(client=client, doc_type=doc_type, image_path=tmp_path)
        return _build_response(res, uid)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


# -------------------------
# FALLBACK: JSON base64
# -------------------------
@router.post("/process_base64", response_model=ProcessResponse)
def process_base64(req: ProcessRequest) -> dict:
    uid = (req.uid or "").strip()
    if not uid:
        raise HTTPException(status_code=422, detail="uid must not be empty.")

    raw = _strip_data_url(req.file_base64)
    try:
        blob = base64.b64decode(raw, validate=True)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="Invalid base64 payload.")

    if not blob:
        raise HTTPException(status_code=400, detail="Decoded file is empty.")

    ext = _choose_ext(
        req_ext=req.extension,
        blob=blob,
        filename=None,
        content_type=None,
    )

    limit = _max_bytes_for_ext(ext)
    if len(blob) > limit:
        raise HTTPException(status_code=413, detail=f"File too large. Max bytes for .{ext} = {limit}.")

    tmp_path = _write_temp_bytes(blob, ext)
    try:
        client = get_mistral_client()
        res = process_document(client=client, doc_type=req.doc_type, image_path=tmp_path)
        return _build_response(res, uid)
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
