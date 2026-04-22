from __future__ import annotations

import argparse
import logging

import ee
import pandas as pd

from .utils import (
    format_month_label,
    initialize_earth_engine,
    load_boundary_geojson,
    geojson_to_ee_geometry,
    log_message,
    normalize_month_value,
)

GLDAS_DATASET = "NASA/GLDAS/V021/NOAH/G025/T3H"
GLDAS_SCALE_METERS = 27_830
THREE_HOUR_SECONDS = 10_800
GLDAS_OUTPUT_COLUMNS = [
    "date",
    "year",
    "month",
    "gldas_precip",
    "gldas_soil_moisture",
    "gldas_et",
    "gldas_air_temp",
    "source_dataset",
]

PREFERRED_PRECIP_BANDS = ("Rainf_f_tavg", "Rainf_tavg")
PREFERRED_ET_BANDS = ("Evap_tavg", "Qle_tavg")
PREFERRED_AIR_TEMP_BANDS = ("Tair_f_inst", "AvgSurfT_inst")
SOIL_MOISTURE_LAYER_BANDS = [
    "SoilMoi0_10cm_inst",
    "SoilMoi10_40cm_inst",
    "SoilMoi40_100cm_inst",
    "SoilMoi100_200cm_inst",
]
SOIL_MOISTURE_FALLBACK_BAND = "RootMoist_inst"


def get_gldas_collection() -> ee.ImageCollection:
    return ee.ImageCollection(GLDAS_DATASET)


def inspect_gldas_bands(collection: ee.ImageCollection | None = None) -> list[str]:
    target_collection = collection or get_gldas_collection()
    first_image = ee.Image(target_collection.first())
    bands = first_image.bandNames().getInfo()
    if not bands:
        raise RuntimeError("GLDAS collection returned no bands.")
    return list(bands)


def resolve_gldas_band_config(
    collection: ee.ImageCollection | None = None,
    logger: logging.Logger | None = None,
) -> dict[str, object]:
    available_bands = inspect_gldas_bands(collection)

    precip_band = next((band for band in PREFERRED_PRECIP_BANDS if band in available_bands), None)
    et_band = next((band for band in PREFERRED_ET_BANDS if band in available_bands), None)
    air_temp_band = next((band for band in PREFERRED_AIR_TEMP_BANDS if band in available_bands), None)
    soil_bands = [band for band in SOIL_MOISTURE_LAYER_BANDS if band in available_bands]

    if precip_band is None:
        raise RuntimeError(
            "Unable to find a supported GLDAS precipitation band. "
            f"Available bands were: {available_bands}"
        )

    if et_band is None:
        raise RuntimeError(
            "Unable to find a supported GLDAS evapotranspiration or latent heat band. "
            f"Available bands were: {available_bands}"
        )

    if air_temp_band is None:
        raise RuntimeError(
            "Unable to find a supported GLDAS air temperature band. "
            f"Available bands were: {available_bands}"
        )

    if soil_bands:
        log_message(
            logger,
            "Using GLDAS soil moisture layers: "
            + ", ".join(soil_bands)
            + ". The monthly value is the mean of the summed 0-200 cm layers.",
        )
    elif SOIL_MOISTURE_FALLBACK_BAND in available_bands:
        soil_bands = [SOIL_MOISTURE_FALLBACK_BAND]
        log_message(
            logger,
            "Using GLDAS RootMoist_inst as a fallback soil moisture context variable.",
        )
    else:
        raise RuntimeError(
            "Unable to find supported GLDAS soil moisture bands. "
            f"Available bands were: {available_bands}"
        )

    return {
        "precip_band": precip_band,
        "et_band": et_band,
        "air_temp_band": air_temp_band,
        "soil_bands": soil_bands,
    }


def _build_month_record(
    month_start: pd.Timestamp,
    punjab_geometry: ee.Geometry,
    collection: ee.ImageCollection,
    band_config: dict[str, object],
) -> dict[str, object]:
    start_date = month_start.strftime("%Y-%m-%d")
    end_date = (month_start + pd.offsets.MonthBegin(1)).strftime("%Y-%m-%d")

    month_collection = collection.filterDate(start_date, end_date)
    image_count = month_collection.size().getInfo()
    if image_count == 0:
        return {
            "date": month_start.strftime("%Y-%m-%d"),
            "year": month_start.year,
            "month": month_start.month,
            "gldas_precip": None,
            "gldas_soil_moisture": None,
            "gldas_et": None,
            "gldas_air_temp": None,
            "source_dataset": GLDAS_DATASET,
        }

    precip_band = str(band_config["precip_band"])
    et_band = str(band_config["et_band"])
    air_temp_band = str(band_config["air_temp_band"])
    soil_bands = [str(band) for band in band_config["soil_bands"]]

    # GLDAS precipitation is provided as a 3-hourly rate (kg/m^2/s). Multiplying
    # by 10,800 seconds converts each timestep to depth-equivalent kg/m^2, and
    # summing across the month yields a monthly total that is numerically close to mm.
    precip_total = (
        month_collection.select(precip_band)
        .map(lambda image: ee.Image(image).multiply(THREE_HOUR_SECONDS))
        .sum()
        .rename("gldas_precip")
    )

    # Soil moisture is a state variable. We first sum the available soil layers
    # per timestep to represent a 0-200 cm total moisture column, then average
    # those timestep totals across the month.
    soil_moisture_mean = (
        month_collection.map(
            lambda image: ee.Image(image)
            .select(soil_bands)
            .reduce(ee.Reducer.sum())
            .rename("gldas_soil_moisture")
        )
        .mean()
        .rename("gldas_soil_moisture")
    )

    if et_band == "Evap_tavg":
        # Evap_tavg is a 3-hourly evapotranspiration rate (kg/m^2/s), converted
        # here to a Punjab-wide monthly total depth-equivalent by timestep summation.
        et_image = (
            month_collection.select(et_band)
            .map(lambda image: ee.Image(image).multiply(THREE_HOUR_SECONDS))
            .sum()
            .rename("gldas_et")
        )
    else:
        # If Evap_tavg is unavailable, the closest catalog variable is Qle_tavg.
        # In that fallback case gldas_et becomes a latent heat flux proxy, not ET depth.
        et_image = month_collection.select(et_band).mean().rename("gldas_et")

    # Air temperature is provided in Kelvin. We convert the monthly mean to Celsius
    # to make the stored context variable easier to interpret downstream.
    air_temp_mean = (
        month_collection.select(air_temp_band)
        .mean()
        .subtract(273.15)
        .rename("gldas_air_temp")
    )

    monthly_image = ee.Image.cat(
        [precip_total, soil_moisture_mean, et_image, air_temp_mean]
    )

    stats = monthly_image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=punjab_geometry,
        scale=GLDAS_SCALE_METERS,
        bestEffort=True,
        maxPixels=1e13,
    ).getInfo()

    stats = stats or {}
    return {
        "date": month_start.strftime("%Y-%m-%d"),
        "year": month_start.year,
        "month": month_start.month,
        "gldas_precip": stats.get("gldas_precip"),
        "gldas_soil_moisture": stats.get("gldas_soil_moisture"),
        "gldas_et": stats.get("gldas_et"),
        "gldas_air_temp": stats.get("gldas_air_temp"),
        "source_dataset": GLDAS_DATASET,
    }


def extract_gldas_punjab(
    punjab_geometry: ee.Geometry,
    target_months: list[str],
    logger: logging.Logger | None = None,
) -> pd.DataFrame:
    if not target_months:
        return pd.DataFrame(columns=GLDAS_OUTPUT_COLUMNS)

    collection = get_gldas_collection()
    band_config = resolve_gldas_band_config(collection, logger=logger)

    log_message(
        logger,
        "Using GLDAS bands "
        f"precip={band_config['precip_band']}, "
        f"soil={band_config['soil_bands']}, "
        f"et={band_config['et_band']}, "
        f"air_temp={band_config['air_temp_band']}.",
    )

    normalized_months = sorted({normalize_month_value(month) for month in target_months})
    rows: list[dict[str, object]] = []

    for month_start in normalized_months:
        log_message(logger, f"Extracting GLDAS context for {format_month_label(month_start)}.")
        rows.append(
            _build_month_record(
                month_start=month_start,
                punjab_geometry=punjab_geometry,
                collection=collection,
                band_config=band_config,
            )
        )

    dataframe = pd.DataFrame(rows, columns=GLDAS_OUTPUT_COLUMNS)
    if dataframe.empty:
        return dataframe

    dataframe["date"] = pd.to_datetime(dataframe["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    dataframe["year"] = pd.to_numeric(dataframe["year"], errors="coerce").astype("Int64")
    dataframe["month"] = pd.to_numeric(dataframe["month"], errors="coerce").astype("Int64")

    for column in [
        "gldas_precip",
        "gldas_soil_moisture",
        "gldas_et",
        "gldas_air_temp",
    ]:
        dataframe[column] = pd.to_numeric(dataframe[column], errors="coerce")

    return dataframe.sort_values("date").reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract Punjab-wide GLDAS monthly context.")
    parser.add_argument(
        "--months",
        nargs="+",
        required=True,
        help="One or more target months in YYYY-MM or YYYY-MM-DD format.",
    )
    parser.add_argument(
        "--boundary-path",
        help="Override the default Punjab boundary GeoJSON path.",
    )
    args = parser.parse_args()

    initialize_earth_engine()
    boundary = geojson_to_ee_geometry(load_boundary_geojson(args.boundary_path))
    dataframe = extract_gldas_punjab(boundary, target_months=args.months)
    print(dataframe.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

