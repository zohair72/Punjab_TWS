import { GeoJsonLayer } from "@deck.gl/layers";
import DeckGL from "@deck.gl/react";
import { useEffect, useMemo, useState } from "react";

import { useDashboardData } from "../context/DashboardDataContext";
import { formatMonthLabel, formatNumber } from "../lib/format";

type GeoJsonFeature = {
  geometry?: {
    coordinates?: unknown;
  };
};

type GeoJsonData = {
  features?: GeoJsonFeature[];
};

type FillColor = [number, number, number, number];

type TooltipInfo = {
  x: number;
  y: number;
  object?: { name: string; value: string } | null;
};

function flattenCoordinates(coordinates: unknown, points: number[][] = []) {
  if (!Array.isArray(coordinates)) {
    return points;
  }

  if (
    coordinates.length === 2 &&
    typeof coordinates[0] === "number" &&
    typeof coordinates[1] === "number"
  ) {
    points.push([coordinates[0], coordinates[1]]);
    return points;
  }

  coordinates.forEach((coordinate) => flattenCoordinates(coordinate, points));
  return points;
}

function getBoundaryCenter(data: GeoJsonData | null) {
  const points =
    data?.features?.flatMap((feature) => flattenCoordinates(feature.geometry?.coordinates ?? [])) ?? [];

  if (points.length === 0) {
    return { longitude: 72.7, latitude: 30.9, zoom: 5.8 };
  }

  const longitudes = points.map((point) => point[0]);
  const latitudes = points.map((point) => point[1]);
  const minLng = Math.min(...longitudes);
  const maxLng = Math.max(...longitudes);
  const minLat = Math.min(...latitudes);
  const maxLat = Math.max(...latitudes);

  const span = Math.max(maxLng - minLng, maxLat - minLat);
  const zoom = span > 6 ? 5 : span > 3 ? 6 : 7;

  return {
    longitude: (minLng + maxLng) / 2,
    latitude: (minLat + maxLat) / 2,
    zoom
  };
}

function interpolateColor(
  start: [number, number, number],
  end: [number, number, number],
  ratio: number
): FillColor {
  const safeRatio = Math.max(0, Math.min(1, ratio));
  return [
    Math.round(start[0] + (end[0] - start[0]) * safeRatio),
    Math.round(start[1] + (end[1] - start[1]) * safeRatio),
    Math.round(start[2] + (end[2] - start[2]) * safeRatio),
    180
  ];
}

function MapView() {
  const { selectedRecord, timeseries } = useDashboardData();
  const [boundary, setBoundary] = useState<GeoJsonData | null>(null);
  const [boundaryError, setBoundaryError] = useState<string | null>(null);
  const [tooltip, setTooltip] = useState<TooltipInfo | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadBoundary() {
      try {
        const response = await fetch("/punjab_boundary.geojson");
        if (!response.ok) {
          throw new Error("Could not load Punjab boundary asset.");
        }

        const json = (await response.json()) as GeoJsonData;
        if (!cancelled) {
          setBoundary(json);
          setBoundaryError(null);
        }
      } catch (error) {
        if (!cancelled) {
          setBoundaryError(error instanceof Error ? error.message : "Boundary load failed.");
        }
      }
    }

    void loadBoundary();
    return () => {
      cancelled = true;
    };
  }, []);

  const viewState = useMemo(() => getBoundaryCenter(boundary), [boundary]);

  const metricStats = useMemo(() => {
    const values = timeseries
      .map((record) => record.grace_twsa_cm)
      .filter((value): value is number => value != null && !Number.isNaN(value));

    if (values.length === 0) {
      return { min: null, max: null };
    }

    return {
      min: Math.min(...values),
      max: Math.max(...values)
    };
  }, [timeseries]);

  const regionFillColor = useMemo<FillColor>(() => {
    const value = selectedRecord?.grace_twsa_cm ?? null;
    if (value == null) {
      return [103, 108, 104, 150] as FillColor;
    }

    if (value <= -10) {
      return [190, 77, 66, 185] as FillColor;
    }

    if (value < 0) {
      const ratio = (value + 10) / 10;
      return interpolateColor([190, 77, 66], [227, 185, 74], ratio);
    }

    if (metricStats.max == null || metricStats.max <= 0) {
      return [227, 185, 74, 180] as FillColor;
    }

    const upperBound = Math.max(metricStats.max, 5);
    const ratio = Math.min(value / upperBound, 1);
    return interpolateColor([227, 185, 74], [69, 143, 116], ratio);
  }, [metricStats.max, selectedRecord]);

  const layers = useMemo(
    () => [
      new GeoJsonLayer({
        id: "punjab-boundary",
        data: (boundary ?? undefined) as never,
        filled: true,
        stroked: true,
        lineWidthMinPixels: 2,
        getFillColor: regionFillColor,
        getLineColor: [244, 238, 230, 210],
        pickable: true,
        onHover: (info) => {
          if (info.object) {
            setTooltip({
              x: info.x,
              y: info.y,
              object: {
                name: "Punjab province boundary",
                value: selectedRecord
                  ? `${formatMonthLabel(selectedRecord.date)} | TWSA ${formatNumber(selectedRecord.grace_twsa_cm, { suffix: " cm" })}`
                  : "Reference geometry only. District-level analytics are intentionally excluded."
              }
            });
          } else {
            setTooltip(null);
          }
        }
      })
    ],
    [boundary, regionFillColor, selectedRecord]
  );

  const legendItems = useMemo(() => {
    return [
      { color: "bg-rose-500", label: "Negative anomaly: less stored water than average" },
      { color: "bg-amber-400", label: "Moderate anomaly: near average or mildly stressed" },
      { color: "bg-emerald-500", label: "Positive anomaly: more stored water than average" }
    ];
  }, []);

  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">
            Deck.gl Map
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-cream">Punjab-wide regional condition map</h2>
        </div>
        <div className="rounded-full border border-white/10 bg-obsidian/45 px-4 py-2 text-sm text-cream/75">
          Province-wide fill, not district-level variation
        </div>
      </div>

      <div className="relative overflow-hidden rounded-[24px] border border-white/10 bg-obsidian/80">
        <div className="h-[420px]">
          <DeckGL
            controller
            getTooltip={() => null}
            initialViewState={viewState}
            layers={layers}
          />
        </div>

        {boundaryError ? (
          <div className="absolute inset-x-4 top-4 rounded-2xl bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {boundaryError}
          </div>
        ) : null}

        {!boundaryError && selectedRecord ? (
          <div className="pointer-events-none absolute left-4 top-4 rounded-2xl border border-brass/20 bg-obsidian/85 px-4 py-3 text-sm text-cream/75">
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">Selected month</p>
            <p className="mt-2 text-lg font-medium text-cream">{formatMonthLabel(selectedRecord.date)}</p>
            <p className="mt-1">
              {`TWS anomaly: ${formatNumber(selectedRecord.grace_twsa_cm, { suffix: " cm" })}`}
            </p>
          </div>
        ) : null}

        <div className="absolute bottom-4 right-4 rounded-2xl border border-white/10 bg-obsidian/90 px-4 py-3 text-sm text-cream/75">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">Legend</p>
          <div className="mt-3 grid gap-2">
            {legendItems.map((item) => (
              <div className="flex items-center gap-3" key={item.label}>
                <span className={`h-3.5 w-3.5 rounded-full ${item.color}`} />
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </div>

        {tooltip?.object ? (
          <div
            className="pointer-events-none absolute z-10 max-w-sm rounded-2xl border border-white/10 bg-obsidian/95 px-4 py-3 text-sm text-cream shadow-glow"
            style={{ left: tooltip.x + 16, top: tooltip.y + 16 }}
          >
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">
              {tooltip.object.name}
            </p>
            <p className="mt-2 text-cream/80">{tooltip.object.value}</p>
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default MapView;
