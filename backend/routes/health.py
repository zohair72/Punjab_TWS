from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

try:
    from ..services.data_loader import data_loader
except ImportError:  # pragma: no cover - supports running inside backend/ directly.
    from services.data_loader import data_loader

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    data_loaded: bool
    load_error: str | None = None


@router.get("", response_model=HealthResponse)
def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        data_loaded=data_loader.is_data_loaded(),
        load_error=data_loader.get_load_error(),
    )
