# Backend

This folder contains the FastAPI service for the Punjab Groundwater Stress Dashboard.

## What It Serves

The backend serves **stored processed outputs only**.

- It reads `data/processed/punjab_monthly_timeseries.csv`
- It reads `data/processed/metadata.json`
- It does **not** query Google Earth Engine during API requests

This keeps frontend page loads fast and ensures the dashboard is driven by reproducible pipeline outputs.

## Environment Setup

From the repo root `D:/Punjab TWS`:

```bash
1. Create a virtual environment:
   python -m venv .venv

2. Activate the environment:
   .venv\Scripts\activate
   source .venv/bin/activate

3. Install dependencies:
   pip install -r backend/requirements.txt

4. Run the FastAPI server:
   uvicorn backend.main:app --reload
```

Windows uses:

```bash
.venv\Scripts\activate
```

Linux/macOS uses:

```bash
source .venv/bin/activate
```

## Run Locally

From the repo root:

```bash
uvicorn backend.main:app --reload
```

If Windows file watching is finicky in your environment, this fallback can help:

```bash
set WATCHFILES_FORCE_POLLING=true
uvicorn backend.main:app --reload
```

If you still see Windows `ProactorBasePipeTransport` disconnect tracebacks, use the
Windows-safe launcher instead:

```bash
.\.venv\Scripts\python.exe -m backend.run_dev
```

## Example Commands

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/summary/latest
```

## Configuration

Supported environment variables:

- `API_HOST`
- `API_PORT`
- `DATA_DIR`
- `PROCESSED_CSV_PATH`
- `METADATA_PATH`
- `FRONTEND_ORIGIN`

Defaults are set for local development so the API can run immediately after installing dependencies.

## Notes

- If processed files do not exist yet, `/health` still responds successfully.
- Data endpoints return clear file-related errors until the data pipeline has generated outputs.
- This backend is intentionally file-backed for now so the next step can focus on wiring the React frontend cleanly.
- Install dependencies from the repo root with `pip install -r backend/requirements.txt`; the file lives in `backend/`, not `backend/__pycache__/`.
