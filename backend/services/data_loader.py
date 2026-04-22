from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any

import pandas as pd

try:
    from ..config import settings
except ImportError:  # pragma: no cover - supports running inside backend/ directly.
    from config import settings

TIMESERIES_COLUMNS = [
    "date",
    "year",
    "month",
    "grace_twsa_cm",
    "gldas_precip",
    "gldas_soil_moisture",
    "gldas_et",
    "gldas_air_temp",
]


class DataFilesMissingError(FileNotFoundError):
    """Raised when processed dashboard files have not been generated yet."""


@dataclass
class CachedData:
    dataframe: pd.DataFrame | None = None
    metadata: dict[str, Any] | None = None
    loaded: bool = False
    load_error: str | None = None


class ProcessedDataLoader:
    def __init__(self, csv_path: Path, metadata_path: Path) -> None:
        self.csv_path = csv_path
        self.metadata_path = metadata_path
        self._lock = Lock()
        self._cache = CachedData()

    def _normalize_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        if dataframe.empty:
            return pd.DataFrame(columns=TIMESERIES_COLUMNS)

        normalized = dataframe.copy()
        for column in TIMESERIES_COLUMNS:
            if column not in normalized.columns:
                normalized[column] = pd.NA

        normalized = normalized[TIMESERIES_COLUMNS].copy()
        normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
        normalized = normalized.dropna(subset=["date"])
        normalized["date"] = normalized["date"].dt.strftime("%Y-%m-%d")
        normalized["year"] = pd.to_numeric(normalized["year"], errors="coerce").astype("Int64")
        normalized["month"] = pd.to_numeric(normalized["month"], errors="coerce").astype("Int64")

        for column in [
            "grace_twsa_cm",
            "gldas_precip",
            "gldas_soil_moisture",
            "gldas_et",
            "gldas_air_temp",
        ]:
            normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

        normalized = normalized.sort_values("date").drop_duplicates(subset="date", keep="last")
        return normalized.reset_index(drop=True)

    def _read_dataframe(self) -> pd.DataFrame:
        if not self.csv_path.exists():
            raise DataFilesMissingError(
                f"Processed CSV not found at {self.csv_path}. "
                "Run the data pipeline sync before requesting summary endpoints."
            )

        dataframe = pd.read_csv(self.csv_path)
        return self._normalize_dataframe(dataframe)

    def _read_metadata(self) -> dict[str, Any]:
        if not self.metadata_path.exists():
            return {}

        with self.metadata_path.open("r", encoding="utf-8") as handle:
            content = json.load(handle)
        return content if isinstance(content, dict) else {}

    def refresh_cache(self) -> dict[str, Any]:
        with self._lock:
            try:
                dataframe = self._read_dataframe()
                metadata = self._read_metadata()
            except Exception as exc:
                self._cache = CachedData(
                    dataframe=None,
                    metadata=None,
                    loaded=False,
                    load_error=str(exc),
                )
                raise

            self._cache = CachedData(
                dataframe=dataframe,
                metadata=metadata,
                loaded=True,
                load_error=None,
            )
            return {
                "message": "Cache refreshed successfully.",
                "row_count": int(len(dataframe)),
                "metadata_available": bool(metadata),
            }

    def _ensure_loaded(self) -> None:
        if self._cache.loaded and self._cache.dataframe is not None:
            return

        try:
            self.refresh_cache()
        except DataFilesMissingError:
            raise
        except Exception as exc:
            raise RuntimeError(f"Failed to load processed dashboard data: {exc}") from exc

    def is_data_loaded(self) -> bool:
        if self._cache.loaded and self._cache.dataframe is not None:
            return True
        return self.csv_path.exists()

    def get_load_error(self) -> str | None:
        return self._cache.load_error

    def get_full_timeseries(self) -> pd.DataFrame:
        self._ensure_loaded()
        assert self._cache.dataframe is not None
        return self._cache.dataframe.copy()

    def get_timeline(self) -> list[dict[str, Any]]:
        dataframe = self.get_full_timeseries()
        return [
            {
                "year": int(record["year"]) if pd.notna(record["year"]) else None,
                "month": int(record["month"]) if pd.notna(record["month"]) else None,
                "date": record["date"],
            }
            for record in dataframe[["year", "month", "date"]].to_dict(orient="records")
        ]

    def _serialize_record(self, record: dict[str, Any]) -> dict[str, Any]:
        return {
            key: (None if pd.isna(value) else int(value) if key in {"year", "month"} else value)
            for key, value in record.items()
        }

    def get_latest_record(self) -> dict[str, Any]:
        dataframe = self.get_full_timeseries()
        if dataframe.empty:
            raise DataFilesMissingError("Processed CSV exists but contains no monthly records.")
        latest = dataframe.iloc[-1].to_dict()
        return self._serialize_record(latest)

    def get_summary_stats(self) -> dict[str, Any]:
        dataframe = self.get_full_timeseries()
        if dataframe.empty:
            raise DataFilesMissingError("Processed CSV exists but contains no monthly records.")

        grace_series = dataframe["grace_twsa_cm"].dropna()
        latest_record = self.get_latest_record()
        return {
            "row_count": int(len(dataframe)),
            "start_date": dataframe.iloc[0]["date"],
            "end_date": dataframe.iloc[-1]["date"],
            "grace_min": None if grace_series.empty else float(grace_series.min()),
            "grace_max": None if grace_series.empty else float(grace_series.max()),
            "grace_mean": None if grace_series.empty else float(grace_series.mean()),
            "latest_grace_twsa_cm": latest_record.get("grace_twsa_cm"),
        }

    def get_metadata(self) -> dict[str, Any]:
        if self._cache.loaded and self._cache.metadata is not None:
            return dict(self._cache.metadata)

        if self.metadata_path.exists():
            return self._read_metadata()

        return {}

    def get_record_by_date(self, year: int, month: int) -> dict[str, Any]:
        dataframe = self.get_full_timeseries()
        match = dataframe[
            (dataframe["year"] == year) &
            (dataframe["month"] == month)
        ]
        if match.empty:
            raise KeyError(f"No monthly record found for year={year}, month={month}.")
        return self._serialize_record(match.iloc[0].to_dict())


data_loader = ProcessedDataLoader(
    csv_path=settings.processed_csv_path,
    metadata_path=settings.metadata_path,
)
