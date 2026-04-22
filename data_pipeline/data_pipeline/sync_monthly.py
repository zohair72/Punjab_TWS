import pandas as pd
from pathlib import Path

from .extract_gldas_punjab import GLDAS_DATASET, extract_gldas_punjab
from .extract_grace_punjab import (
    GRACE_DATASET,
    extract_grace_punjab,
    list_grace_available_months,
)
from .utils import (
    MERGED_OUTPUT_COLUMNS,
    configure_logger,
    format_month_label,
    geojson_to_ee_geometry,
    get_boundary_path,
    get_output_dir,
    initialize_earth_engine,
    latest_stored_month,
    load_boundary_geojson,
    log_message,
    read_existing_processed_csv,
    utc_now_iso,
    write_metadata,
    write_processed_outputs,
)


def _merge_new_data(
    existing: pd.DataFrame,
    new_grace: pd.DataFrame,
    new_gldas: pd.DataFrame,
) -> pd.DataFrame:
    merged_new = pd.merge(
        new_grace,
        new_gldas,
        on=["date", "year", "month"],
        how="left",
        suffixes=("", "_gldas"),
    )

    merged_new = merged_new[
        [
            "date",
            "year",
            "month",
            "grace_twsa_cm",
            "gldas_precip",
            "gldas_soil_moisture",
            "gldas_et",
            "gldas_air_temp",
        ]
    ]

    frames_to_concat = [frame for frame in (existing, merged_new) if not frame.empty]
    combined = (
        pd.concat(frames_to_concat, ignore_index=True)
        if frames_to_concat
        else pd.DataFrame(columns=MERGED_OUTPUT_COLUMNS)
    )
    combined = combined.sort_values("date").drop_duplicates(subset="date", keep="last")
    return combined[MERGED_OUTPUT_COLUMNS].reset_index(drop=True)


def run_monthly_sync(
    boundary_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    full_refresh: bool = False,
    logger=None,
) -> dict[str, object]:
    resolved_output_dir = Path(output_dir) if output_dir else get_output_dir()
    csv_path = resolved_output_dir / "punjab_monthly_timeseries.csv"
    json_path = resolved_output_dir / "punjab_monthly_timeseries.json"
    metadata_path = resolved_output_dir / "metadata.json"

    initialize_earth_engine(logger=logger)
    resolved_boundary_path = get_boundary_path(boundary_path)
    boundary_geojson = load_boundary_geojson(resolved_boundary_path)
    punjab_geometry = geojson_to_ee_geometry(boundary_geojson)
    log_message(logger, f"Using Punjab boundary file: {resolved_boundary_path}")

    existing = pd.DataFrame(columns=MERGED_OUTPUT_COLUMNS)
    if not full_refresh:
        existing = read_existing_processed_csv(csv_path)

    stored_month = None if full_refresh else latest_stored_month(existing)
    if stored_month:
        log_message(
            logger,
            f"Latest stored GRACE month in processed output: {format_month_label(stored_month)}.",
        )
    elif full_refresh:
        log_message(logger, "Full refresh requested; existing processed data will be ignored.")
    else:
        log_message(logger, "No existing processed CSV found. Running first historical extraction.")

    new_grace_months = list_grace_available_months(latest_stored_month=stored_month)
    if not new_grace_months:
        message = "No update needed. Stored data already includes the latest available GRACE month."
        log_message(logger, message)
        return {
            "status": "no_update_needed",
            "new_months": [],
            "csv_path": str(csv_path),
            "json_path": str(json_path),
            "metadata_path": str(metadata_path),
        }

    log_message(
        logger,
        "New GRACE months detected: "
        + ", ".join(format_month_label(month) for month in new_grace_months),
    )

    grace_dataframe = extract_grace_punjab(
        punjab_geometry=punjab_geometry,
        latest_stored_month=stored_month,
        logger=logger,
    )

    if grace_dataframe.empty:
        message = "GRACE reported new months, but extraction returned no rows."
        log_message(logger, message)
        return {
            "status": "grace_empty",
            "new_months": [format_month_label(month) for month in new_grace_months],
            "csv_path": str(csv_path),
            "json_path": str(json_path),
            "metadata_path": str(metadata_path),
        }

    target_months = grace_dataframe["date"].tolist()
    gldas_dataframe = extract_gldas_punjab(
        punjab_geometry=punjab_geometry,
        target_months=target_months,
        logger=logger,
    )

    combined = _merge_new_data(existing, grace_dataframe, gldas_dataframe)
    combined = write_processed_outputs(combined, csv_path=csv_path, json_path=json_path)

    latest_month_value = latest_stored_month(combined)
    metadata = {
        "latest_grace_month": format_month_label(latest_month_value) if latest_month_value else None,
        "row_count": int(len(combined)),
        "last_synced_at": utc_now_iso(),
        "datasets_used": [GRACE_DATASET, GLDAS_DATASET],
        "boundary_path": str(resolved_boundary_path),
    }
    write_metadata(metadata_path, metadata)

    log_message(logger, f"Monthly sync complete. Wrote {len(combined)} rows to {csv_path}.")
    return {
        "status": "updated",
        "new_months": [format_month_label(month) for month in new_grace_months],
        "row_count": len(combined),
        "csv_path": str(csv_path),
        "json_path": str(json_path),
        "metadata_path": str(metadata_path),
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Sync Punjab-wide GRACE TWS anomaly and matching GLDAS context."
    )
    parser.add_argument(
        "--boundary-path",
        default=None,
        help=(
            "Path to the Punjab province boundary GeoJSON. "
            "If omitted, BOUNDARY_PATH from .env or a default boundary path is used."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default=str(get_output_dir()),
        help="Directory for processed CSV/JSON outputs.",
    )
    parser.add_argument(
        "--full-refresh",
        action="store_true",
        help="Ignore existing processed data and rebuild the full time series.",
    )
    args = parser.parse_args()

    resolved_output_dir = Path(args.output_dir)
    logger = configure_logger(resolved_output_dir / "sync.log")

    try:
        result = run_monthly_sync(
            boundary_path=args.boundary_path,
            output_dir=resolved_output_dir,
            full_refresh=args.full_refresh,
            logger=logger,
        )
    except FileNotFoundError as exc:
        log_message(logger, f"Boundary file error: {exc}")
        return 1
    except RuntimeError as exc:
        log_message(logger, str(exc))
        return 1
    except Exception as exc:  # pragma: no cover - defensive CLI guard.
        log_message(logger, f"Unexpected sync failure: {exc}")
        return 1

    if result["status"] == "updated":
        log_message(logger, "Processed CSV, JSON, metadata, and sync log are up to date.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
