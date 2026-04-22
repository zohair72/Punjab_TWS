# Frontend

This folder contains the React + Vite + TypeScript dashboard client for the Punjab Groundwater Stress Dashboard.

## Stack

- React
- Vite
- TypeScript
- TailwindCSS
- Recharts
- Deck.gl
- React Router

## Responsibilities

- Read processed outputs from the FastAPI backend.
- Render Punjab-scale summary cards, time series, methodology, and map views.
- Keep the dashboard focused on Punjab-wide interpretation rather than district analytics.

## Local Development

From the repo root:

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at:

```bash
http://localhost:8000
```

Override that with:

```bash
VITE_API_BASE_URL=https://your-backend-url
```

## Build

```bash
npm run build
```

## Deployment Notes

This app is ready to deploy to Vercel or Netlify once you set:

```bash
VITE_API_BASE_URL=https://your-deployed-fastapi-backend
```

The frontend does not call Earth Engine directly. It only reads stored processed outputs through the FastAPI API.
