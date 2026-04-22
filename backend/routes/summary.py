from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

try:
    from ..services.data_loader import DataFilesMissingError, data_loader
except ImportError:  # pragma: no cover - supports running inside backend/ directly.
    from services.data_loader import DataFilesMissingError, data_loader

router = APIRouter()


class MonthlySummaryRecord(BaseModel):
    date: str
    year: int | None
    month: int | None
    grace_twsa_cm: float | None
    gldas_precip: float | None
    gldas_soil_moisture: float | None
    gldas_et: float | None
    gldas_air_temp: float | None


class SummaryStatsResponse(BaseModel):
    row_count: int
    start_date: str
    end_date: str
    grace_min: float | None
    grace_max: float | None
    grace_mean: float | None
    latest_grace_twsa_cm: float | None


class RefreshResponse(BaseModel):
    message: str
    row_count: int | None = None
    metadata_available: bool | None = None


def _raise_data_error(exc: Exception) -> None:
    if isinstance(exc, DataFilesMissingError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/latest", response_model=MonthlySummaryRecord)
def get_latest_record() -> MonthlySummaryRecord:
    try:
        record = data_loader.get_latest_record()
    except Exception as exc:
        _raise_data_error(exc)
    return MonthlySummaryRecord(**record)


@router.get("/timeseries", response_model=list[MonthlySummaryRecord])
def get_full_timeseries() -> list[MonthlySummaryRecord]:
    try:
        dataframe = data_loader.get_full_timeseries()
    except Exception as exc:
        _raise_data_error(exc)

    records = dataframe.astype(object).where(dataframe.notna(), None).to_dict(orient="records")
    return [MonthlySummaryRecord(**record) for record in records]


@router.get("/by-date", response_model=MonthlySummaryRecord)
def get_record_by_date(
    year: int = Query(..., ge=1900, le=2500),
    month: int = Query(..., ge=1, le=12),
) -> MonthlySummaryRecord:
    try:
        record = data_loader.get_record_by_date(year=year, month=month)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        _raise_data_error(exc)

    return MonthlySummaryRecord(**record)


@router.get("/stats", response_model=SummaryStatsResponse)
def get_summary_stats() -> SummaryStatsResponse:
    try:
        stats = data_loader.get_summary_stats()
    except Exception as exc:
        _raise_data_error(exc)
    return SummaryStatsResponse(**stats)


@router.get("/refresh", response_model=RefreshResponse)
def refresh_cache() -> RefreshResponse:
    try:
        result = data_loader.refresh_cache()
    except Exception as exc:
        _raise_data_error(exc)
    return RefreshResponse(**result)
