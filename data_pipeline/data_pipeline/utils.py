from __future__ import annotations

import json
import logging
import os
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Mapping

import ee
import pandas as pd
from dotenv import load_dotenv

MERGED_OUTPUT_COLUMNS = [
    "date",
    "year",
    "month",
    "grace_twsa_cm",
    "gldas_precip",
    "gldas_soil_moisture",
    "gldas_et",
    "gldas_air_temp",
]


def get_repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_environment() -> None:
    """Load repo-level environment variables if a local .env file exists."""
    load_dotenv(get_repo_root() / ".env", override=False)


def resolve_repo_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return get_repo_root() / path


def get_data_dir() -> Path:
    load_environment()
    configured = os.getenv("DATA_DIR", "data")
    return resolve_repo_path(configured)


def get_output_dir() -> Path:
    load_environment()
    configured = os.getenv("OUTPUT_DIR", "data/processed")
    return resolve_repo_path(configured)


def get_boundary_path(boundary_path: str | Path | None = None) -> Path:
    if boundary_path is not None:
        return resolve_repo_path(boundary_path)

    load_environment()
    configured_boundary = os.getenv("BOUNDARY_PATH")
    if configured_boundary:
        return resolve_repo_path(configured_boundary)

    data_dir = get_data_dir()
    candidates = [
        data_dir / "boundaries" / "punjab_boundary.geojson",
        data_dir / "boundaries" / "punjab_boundaries" / "Punjab_Provincial_Boundary.geojson",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def configure_logger(log_path: Path, logger_name: str = "punjab_groundwater_sync") -> logging.Logger:
    ensure_directory(log_path.parent)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def log_message(logger: logging.Logger | None, message: str) -> None:
    if logger is not None:
        logger.info(message)
    else:
        print(message)


def initialize_earth_engine(
    project: str | None = None,
    logger: logging.Logger | None = None,
) -> None:
    """
    Initialize the Earth Engine Python client.

    A project is optional but strongly recommended. If initialization fails,
    the raised error includes a practical authentication hint.
    """
    load_environment()
    ee_project = project or os.getenv("EARTH_ENGINE_PROJECT")

    try:
        if ee_project:
            ee.Initialize(project=ee_project)
            log_message(logger, f"Initialized Earth Engine with project '{ee_project}'.")
        else:
            ee.Initialize()
            log_message(
                logger,
                "Initialized Earth Engine without an explicit project. "
                "Set EARTH_ENGINE_PROJECT in .env for production use.",
            )
    except Exception as exc:  # pragma: no cover - depends on runtime auth.
        raise RuntimeError(
            "Earth Engine initialization failed. Run `earthengine authenticate` "
            "and set `EARTH_ENGINE_PROJECT` in your environment or .env file."
        ) from exc


def load_boundary_geojson(boundary_path: str | Path | None = None) -> dict[str, Any]:
    path = get_boundary_path(boundary_path)
    if not path.exists():
        raise FileNotFoundError(
            f"Punjab boundary GeoJSON not found at {path}. "
            "Expected a province-scale boundary file for Punjab-wide aggregation."
        )
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def geojson_to_ee_geometry(geojson_data: Mapping[str, Any]) -> ee.Geometry:
    geojson_type = geojson_data.get("type")

    if geojson_type == "FeatureCollection":
        features = geojson_data.get("features", [])
        if not features:
            raise ValueError("Boundary GeoJSON FeatureCollection is empty.")
        return ee.FeatureCollection(geojson_data).geometry()

    if geojson_type == "Feature":
        geometry = geojson_data.get("geometry")
        if geometry is None:
            raise ValueError("Boundary GeoJSON feature is missing its geometry.")
        return ee.Geometry(geometry)

    if geojson_type in {
        "Polygon",
        "MultiPolygon",
        "LineString",
        "MultiLineString",
        "Point",
        "MultiPoint",
        "GeometryCollection",
    }:
        return ee.Geometry(geojson_data)

    raise ValueError(f"Unsupported GeoJSON type for Punjab boundary: {geojson_type}")


def normalize_month_value(value: str | date | datetime | pd.Timestamp) -> pd.Timestamp:
    if isinstance(value, str):
        raw = value.strip()
        if len(raw) == 7:
            raw = f"{raw}-01"
        month = pd.Timestamp(raw)
    else:
        month = pd.Timestamp(value)

    if month.tzinfo is not None:
        month = month.tz_convert(None)

    return month.normalize().replace(day=1)


def format_month_label(value: str | date | datetime | pd.Timestamp) -> str:
    return normalize_month_value(value).strftime("%Y-%m")


def format_date_string(value: str | date | datetime | pd.Timestamp) -> str:
    return normalize_month_value(value).strftime("%Y-%m-%d")


def month_after(value: str | date | datetime | pd.Timestamp) -> pd.Timestamp:
    return normalize_month_value(value) + pd.offsets.MonthBegin(1)


def empty_merged_dataframe() -> pd.DataFrame:
    return pd.DataFrame(columns=MERGED_OUTPUT_COLUMNS)


def read_existing_processed_csv(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        return empty_merged_dataframe()

    dataframe = pd.read_csv(csv_path)
    if dataframe.empty:
        return empty_merged_dataframe()

    for column in MERGED_OUTPUT_COLUMNS:
        if column not in dataframe.columns:
            dataframe[column] = pd.NA

    dataframe = dataframe[MERGED_OUTPUT_COLUMNS].copy()
    dataframe["date"] = pd.to_datetime(dataframe["date"], errors="coerce").dt.strftime("%Y-%m-%d")

    numeric_columns = [column for column in MERGED_OUTPUT_COLUMNS if column != "date"]
    for column in numeric_columns:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    return dataframe


def latest_stored_month(dataframe: pd.DataFrame) -> str | None:
    if dataframe.empty or "date" not in dataframe.columns:
        return None

    month_values = pd.to_datetime(dataframe["date"], errors="coerce").dropna()
    if month_values.empty:
        return None

    return month_values.max().strftime("%Y-%m-%d")


def prepare_output_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    if dataframe.empty:
        return empty_merged_dataframe()

    prepared = dataframe.copy()
    for column in MERGED_OUTPUT_COLUMNS:
        if column not in prepared.columns:
            prepared[column] = pd.NA

    prepared["date"] = pd.to_datetime(prepared["date"], errors="coerce")
    prepared = prepared.dropna(subset=["date"])
    prepared["date"] = prepared["date"].dt.strftime("%Y-%m-%d")
    prepared["year"] = pd.to_numeric(prepared["year"], errors="coerce").astype("Int64")
    prepared["month"] = pd.to_numeric(prepared["month"], errors="coerce").astype("Int64")

    float_columns = [
        "grace_twsa_cm",
        "gldas_precip",
        "gldas_soil_moisture",
        "gldas_et",
        "gldas_air_temp",
    ]
    for column in float_columns:
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce")

    prepared = prepared[MERGED_OUTPUT_COLUMNS]
    prepared = prepared.sort_values("date").drop_duplicates(subset="date", keep="last")
    return prepared.reset_index(drop=True)


def dataframe_to_records(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    prepared = prepare_output_dataframe(dataframe)
    serializable = prepared.astype(object).where(pd.notnull(prepared), None)
    return serializable.to_dict(orient="records")


def write_json(path: Path, payload: Any) -> None:
    ensure_directory(path.parent)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_processed_outputs(dataframe: pd.DataFrame, csv_path: Path, json_path: Path) -> pd.DataFrame:
    prepared = prepare_output_dataframe(dataframe)
    ensure_directory(csv_path.parent)
    prepared.to_csv(csv_path, index=False)
    write_json(json_path, dataframe_to_records(prepared))
    return prepared


def write_metadata(metadata_path: Path, payload: Mapping[str, Any]) -> None:
    write_json(metadata_path, dict(payload))


def utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()
