from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
from ocr_service.core.types import OCRResult

class DocumentProcessor(ABC):
    """
    Each doc_type has a processor.
    For now, processors can be stubs; later they implement extraction logic.
    """
    @property
    @abstractmethod
    def doc_type(self) -> str:
        raise NotImplementedError
    
    @abstractmethod
    def extract_fields(self, ocr: OCRResult) -> Dict[str, Any]:
        """
        Return extracted fields only. Stub returns empty values.
        """
        raise NotImplementedError
