from __future__ import annotations
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    mistral_api_key: str
    confidence_threshold: float = 0.75
    ocr_cache_enabled: bool = True
    ocr_cache_dir: str = "cache/ocr"
    ocr_cache_force_refresh: bool = False
    ocr_model: str = "mistral-ocr-latest"
    ocr_table_format: str = "markdown"


def get_settings() -> Settings:
    api_key = os.getenv("MISTRAL_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("MISTRAL_API_KEY is missing (check .env or environment variables).")
    return Settings(
        mistral_api_key=api_key,
        confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.75")),
        ocr_cache_enabled=os.getenv("OCR_CACHE_ENABLED", "1") == "1",
        ocr_cache_dir=os.getenv("OCR_CACHE_DIR", "cache/ocr"),
        ocr_cache_force_refresh=os.getenv("OCR_CACHE_FORCE_REFRESH", "0") == "1",
        ocr_model=os.getenv("OCR_MODEL", "mistral-ocr-latest"),
        ocr_table_format=os.getenv("OCR_TABLE_FORMAT", "markdown"),
    )
