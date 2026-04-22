from __future__ import annotations

import argparse
import logging
from typing import Any

import ee
import pandas as pd

from .utils import (
    format_month_label,
    initialize_earth_engine,
    load_boundary_geojson,
    geojson_to_ee_geometry,
    log_message,
    month_after,
)

GRACE_DATASET = "NASA/GRACE/MASS_GRIDS_V04/MASCON"
GRACE_SCALE_METERS = 55_660
GRACE_TWSA_BAND_CANDIDATES = ("lwe_thickness",)
GRACE_OUTPUT_COLUMNS = [
    "date",
    "year",
    "month",
    "grace_twsa_cm",
    "source_dataset",
]


def get_grace_collection() -> ee.ImageCollection:
    return ee.ImageCollection(GRACE_DATASET)


def inspect_grace_bands(collection: ee.ImageCollection | None = None) -> list[str]:
    target_collection = collection or get_grace_collection()
    first_image = ee.Image(target_collection.first())
    bands = first_image.bandNames().getInfo()
    if not bands:
        raise RuntimeError("GRACE collection returned no bands.")
    return list(bands)


def resolve_grace_twsa_band(collection: ee.ImageCollection | None = None) -> str:
    available_bands = inspect_grace_bands(collection)
    for candidate in GRACE_TWSA_BAND_CANDIDATES:
        if candidate in available_bands:
            return candidate
    raise RuntimeError(
        "Unable to find a supported GRACE terrestrial water storage anomaly band. "
        f"Available bands were: {available_bands}"
    )


def list_grace_available_months(latest_stored_month: str | None = None) -> list[str]:
    collection = get_grace_collection()
    if latest_stored_month:
        collection = collection.filterDate(
            month_after(latest_stored_month).strftime("%Y-%m-%d"),
            "2100-01-01",
        )

    timestamps = collection.aggregate_array("system:time_start").getInfo() or []
    month_strings = {
        pd.to_datetime(timestamp, unit="ms", utc=True).strftime("%Y-%m-01")
        for timestamp in timestamps
    }
    return sorted(month_strings)


def _image_to_feature(
    image: ee.Image,
    punjab_geometry: ee.Geometry,
    band_name: str,
) -> ee.Feature:
    image_date = image.date()

    # `lwe_thickness` is the GRACE/GRACE-FO equivalent liquid water thickness
    # anomaly in centimeters. Here we reduce it to a Punjab-wide monthly mean.
    stats = image.select(band_name).reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=punjab_geometry,
        scale=GRACE_SCALE_METERS,
        bestEffort=True,
        maxPixels=1e13,
    )

    return ee.Feature(
        None,
        {
            "date": image_date.format("YYYY-MM-01"),
            "year": ee.Number.parse(image_date.format("YYYY")),
            "month": ee.Number.parse(image_date.format("M")),
            "grace_twsa_cm": stats.get(band_name),
            "source_dataset": GRACE_DATASET,
        },
    )


def extract_grace_punjab(
    punjab_geometry: ee.Geometry,
    latest_stored_month: str | None = None,
    logger: logging.Logger | None = None,
) -> pd.DataFrame:
    collection = get_grace_collection()
    band_name = resolve_grace_twsa_band(collection)

    if latest_stored_month:
        start_date = month_after(latest_stored_month).strftime("%Y-%m-%d")
        collection = collection.filterDate(start_date, "2100-01-01")
        log_message(
            logger,
            f"Filtering GRACE extraction to months after {format_month_label(latest_stored_month)}.",
        )

    image_count = collection.size().getInfo()
    if image_count == 0:
        log_message(logger, "No GRACE images matched the requested extraction window.")
        return pd.DataFrame(columns=GRACE_OUTPUT_COLUMNS)

    log_message(
        logger,
        f"Using GRACE band '{band_name}' from {GRACE_DATASET} across {image_count} monthly images.",
    )

    feature_collection = ee.FeatureCollection(
        collection.map(lambda image: _image_to_feature(ee.Image(image), punjab_geometry, band_name))
    )

    try:
        feature_info = feature_collection.getInfo()
    except Exception as exc:  # pragma: no cover - EE runtime specific.
        raise RuntimeError("Failed to extract the Punjab-wide GRACE time series.") from exc

    rows: list[dict[str, Any]] = []
    for feature in feature_info.get("features", []):
        properties = feature.get("properties", {})
        rows.append(
            {
                "date": properties.get("date"),
                "year": properties.get("year"),
                "month": properties.get("month"),
                "grace_twsa_cm": properties.get("grace_twsa_cm"),
                "source_dataset": properties.get("source_dataset", GRACE_DATASET),
            }
        )

    dataframe = pd.DataFrame(rows, columns=GRACE_OUTPUT_COLUMNS)
    if dataframe.empty:
        return dataframe

    dataframe["date"] = pd.to_datetime(dataframe["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    dataframe["year"] = pd.to_numeric(dataframe["year"], errors="coerce").astype("Int64")
    dataframe["month"] = pd.to_numeric(dataframe["month"], errors="coerce").astype("Int64")
    dataframe["grace_twsa_cm"] = pd.to_numeric(dataframe["grace_twsa_cm"], errors="coerce")
    return dataframe.sort_values("date").reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract Punjab-wide GRACE TWS anomaly data.")
    parser.add_argument(
        "--latest-stored-month",
        help="Only extract GRACE months after this YYYY-MM or YYYY-MM-DD value.",
    )
    parser.add_argument(
        "--boundary-path",
        help="Override the default Punjab boundary GeoJSON path.",
    )
    args = parser.parse_args()

    initialize_earth_engine()
    boundary = geojson_to_ee_geometry(load_boundary_geojson(args.boundary_path))
    dataframe = extract_grace_punjab(boundary, latest_stored_month=args.latest_stored_month)
    print(dataframe.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

