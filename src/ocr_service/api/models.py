# Pydantic models for request/response.

from __future__ import annotations
from typing import Any, Dict, Optional, Literal
from pydantic import BaseModel, Field
from ocr_service.core.types import DocType

class ProcessRequest(BaseModel):
    doc_type: DocType
    file_base64: str = Field(..., min_length=16)   # base64 or data URL
    extension: Optional[str] = None                # "jpg"/"png"/"pdf"/...
    mime: Optional[str] = None                     # optional explicit MIME

class ProcessResponse(BaseModel):
    doc_type: str
    document_number: Optional[str]
    is_correct_document: bool
    confidence: float
    personal_data: Optional[Dict[str, Any]] = None
    vehicle_data: Optional[Dict[str, Any]] = None
