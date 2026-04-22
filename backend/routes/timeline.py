from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

try:
    from ..services.data_loader import DataFilesMissingError, data_loader
except ImportError:  # pragma: no cover - supports running inside backend/ directly.
    from services.data_loader import DataFilesMissingError, data_loader

router = APIRouter()


class TimelineItem(BaseModel):
    year: int | None
    month: int | None
    date: str


@router.get("", response_model=list[TimelineItem])
def get_timeline() -> list[TimelineItem]:
    try:
        items = data_loader.get_timeline()
    except DataFilesMissingError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return [TimelineItem(**item) for item in items]
