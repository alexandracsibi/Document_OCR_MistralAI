# FastAPI app + include router + health endpoint.
from __future__ import annotations

from fastapi import FastAPI, Response
from ocr_service.api.routes import router

app = FastAPI(title="ocr_service", version="0.1.0")

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

app.include_router(router, prefix="/v1")

@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)