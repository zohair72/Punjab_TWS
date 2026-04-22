# Data Pipeline

This folder contains the Python package responsible for Earth Engine extraction, monthly sync orchestration, and writing stable processed outputs for the dashboard backend.

## Design Intent

- GRACE is the pacing dataset for update detection.
- For each newly available GRACE month, the pipeline stores the matching GLDAS month as context.
- Processed CSV/JSON outputs are written to `data/processed/`.
- The dashboard should read those stored outputs through the API, not call Earth Engine live on each page load.

## Earth Engine Authentication

Authenticate Earth Engine before running the sync:

```bash
earthengine authenticate
```

Set your GCP project in the repo root `.env` file:

```env
EARTH_ENGINE_PROJECT=your-gcp-project-id
```

## Install

From the repo root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r data_pipeline\requirements.txt
pip install -e data_pipeline
```

## Run A Full Historical Extraction

```bash
python data_pipeline/sync_monthly.py --full-refresh
```

## Run An Incremental Monthly Sync

```bash
python data_pipeline/sync_monthly.py
```

That command:

- checks for newly available GRACE months
- extracts only months not already stored
- pulls GLDAS for the exact same months
- updates `data/processed/punjab_monthly_timeseries.csv`
- updates `data/processed/punjab_monthly_timeseries.json`
- updates `data/processed/metadata.json`
- appends logs to `data/processed/sync.log`

## Key Assumptions

- `data/boundaries/punjab_boundary.geojson` is the Punjab province boundary used for aggregation.
- GRACE `lwe_thickness` is used as the Punjab-scale TWS anomaly signal in centimeters.
- GLDAS precipitation and evapotranspiration are aggregated from 3-hourly rates to monthly totals.
- GLDAS soil moisture is the monthly mean of summed 0-200 cm soil moisture layers when those layers are available.
- GLDAS air temperature is stored as a monthly mean in degrees Celsius after converting from Kelvin.

