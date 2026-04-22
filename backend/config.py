from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    repo_root: Path
    docs_dir: Path
    api_title: str
    api_description: str
    api_version: str
    api_host: str
    api_port: int
    data_dir: Path
    processed_csv_path: Path
    metadata_path: Path
    frontend_origins: list[str]
    frontend_origin_regex: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_environment() -> None:
    load_dotenv(_repo_root() / ".env", override=False)


def _resolve_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return _repo_root() / path


def get_settings() -> Settings:
    _load_environment()
    repo_root = _repo_root()
    data_dir = _resolve_path(os.getenv("DATA_DIR", "data"))
    processed_csv_path = _resolve_path(
        os.getenv("PROCESSED_CSV_PATH", str(data_dir / "processed" / "punjab_monthly_timeseries.csv"))
    )
    metadata_path = _resolve_path(
        os.getenv("METADATA_PATH", str(data_dir / "processed" / "metadata.json"))
    )

    configured_origins = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
    frontend_origins = [origin.strip() for origin in configured_origins.split(",") if origin.strip()]

    return Settings(
        repo_root=repo_root,
        docs_dir=repo_root / "docs",
        api_title="Punjab Groundwater Stress Dashboard API",
        api_description=(
            "FastAPI backend serving stored Punjab-scale terrestrial water storage "
            "anomaly outputs and matching GLDAS context from processed files."
        ),
        api_version="0.1.0",
        api_host=os.getenv("API_HOST", "127.0.0.1"),
        api_port=int(os.getenv("API_PORT", "8000")),
        data_dir=data_dir,
        processed_csv_path=processed_csv_path,
        metadata_path=metadata_path,
        frontend_origins=frontend_origins,
        frontend_origin_regex=os.getenv(
            "FRONTEND_ORIGIN_REGEX",
            r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        ),
    )


settings = get_settings()
