# Punjab Groundwater Stress Dashboard

Punjab Groundwater Stress Dashboard is a production-oriented monorepo for an automated Punjab-scale terrestrial water storage anomaly dashboard built around Google Earth Engine extraction and a stored-data dashboard architecture.

## Scientific Scope

This project is intentionally scoped to **Punjab-scale terrestrial water storage (TWS) anomaly**.

- The main scientific output is Punjab-wide monthly TWS anomaly from `NASA/GRACE/MASS_GRIDS_V04/MASCON`.
- `NASA/GLDAS/V021/NOAH/G025/T3H` is used as monthly contextual support for the same month whenever a new GRACE month becomes available.
- GRACE is the pacing dataset for monthly updates.
- District boundaries may appear as optional map overlays only.
- Districts are not analytical units in this project.
- Outputs are intended for regional interpretation and monitoring, not direct groundwater measurement or local aquifer quantification.

## Architecture

The repository is organized as a small monorepo:

```text
project-root/
  frontend/          React + Vite + TypeScript dashboard
  backend/           FastAPI API that serves stored processed outputs
  data_pipeline/     Python package for extraction, transformation, and sync logic
  data/
    raw/             Raw exports and intermediate source snapshots
    processed/       Versionable dashboard-ready CSV/JSON outputs
    boundaries/      Punjab province and district boundary files
  scripts/           Operational helpers and future automation entrypoints
  docs/              Methodology and project documentation
```

Core flow:

1. The data pipeline checks whether a new GRACE month is available.
2. If a new GRACE month exists, the pipeline extracts and stores Punjab-scale GRACE outputs.
3. The pipeline also pulls the matching GLDAS month as contextual support.
4. Processed CSV/JSON outputs are written to `data/processed/`.
5. The backend reads those stored outputs.
6. The frontend reads from the backend, not directly from Earth Engine.

## Current Assumptions

- Boundary data should live under `data/boundaries/`.
- In the current workspace, the existing files are present under `data/boundaries/punjab_boundaries/`; exact file wiring can be finalized in the Earth Engine step.
- Storage begins with CSV/JSON so PostgreSQL can be added later behind clean interfaces.
- The first implementation step is scaffolding only; Earth Engine extraction logic is the next coding step.

## Quick Start

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend default dev URL: `http://localhost:5173`

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend default dev URL: `http://localhost:8000`

### Data Pipeline

```bash
cd data_pipeline
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python -m data_pipeline.sync_monthly
```

## Environment Variables

Copy `.env.example` to `.env` and fill in values as needed:

- `EARTH_ENGINE_PROJECT`
- `MAPBOX_TOKEN`
- `API_BASE_URL`
- `DATA_DIR`
- `OUTPUT_DIR`

## Next Coding Step

Implement the first real extraction path in `data_pipeline`:

1. Authenticate and initialize Google Earth Engine.
2. Load the Punjab province boundary from `data/boundaries/`.
3. Build Punjab-wide monthly GRACE aggregation using the MASCON dataset.
4. Detect the latest available GRACE month.
5. Pull the matching GLDAS month for contextual storage.
6. Write stable processed timeline outputs for the backend to serve.
