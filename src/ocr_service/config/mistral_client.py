from __future__ import annotations
from mistralai import Mistral
from ocr_service.config.settings import get_settings


def get_mistral_client() -> Mistral:
    """
    Factory for Mistral client.
    Created once per process, safe to reuse.
    """
    settings = get_settings()
    return Mistral(api_key=settings.mistral_api_key)
