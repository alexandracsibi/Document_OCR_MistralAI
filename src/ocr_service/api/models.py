from __future__ import annotations
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from ocr_service.core.types import DocType

class ProcessRequest(BaseModel):
    """
    Request model for JSON base64 endpoint (/v1/process_base64).
    """
    uid: str = Field(..., min_length=1, max_length=128)
    doc_type: DocType
    file_base64: str = Field(..., min_length=16)  # base64 or data URL
    extension: Optional[str] = None

class ProcessResponse(BaseModel):
    """
    Response model (shared shape for both endpoints).
    """
    uid: str
    doc_type: str
    document_number: Optional[str]
    is_correct_document: bool
    confidence: float
    personal_data: Optional[Dict[str, Any]] = None
    vehicle_data: Optional[Dict[str, Any]] = None
