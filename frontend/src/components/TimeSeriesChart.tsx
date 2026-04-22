import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

import { useDashboardData } from "../context/DashboardDataContext";
import { formatMonthLabel, formatNumber } from "../lib/format";

function TimeSeriesChart() {
  const { timeseries, selectedDate, loading, dashboardError } = useDashboardData();

  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">
            Punjab Time Series
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-cream">
            GRACE terrestrial water storage anomaly
          </h2>
        </div>
        {selectedDate ? (
          <div className="rounded-full border border-brass/20 bg-brass/10 px-4 py-2 text-sm text-brass">
            Active month: {formatMonthLabel(selectedDate)}
          </div>
        ) : null}
      </div>

      <div className="mt-6 h-[360px]">
        {loading ? (
          <p className="rounded-2xl bg-white/5 px-4 py-3 text-sm text-cream/70">
            Loading time series...
          </p>
        ) : dashboardError && timeseries.length === 0 ? (
          <p className="rounded-2xl bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
            {dashboardError}
          </p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={timeseries} margin={{ top: 10, right: 16, left: -12, bottom: 6 }}>
              <defs>
                <linearGradient id="twsaFill" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#cf9e58" stopOpacity={0.65} />
                  <stop offset="100%" stopColor="#cf9e58" stopOpacity={0.04} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                minTickGap={28}
                tick={{ fill: "rgba(244, 238, 230, 0.72)", fontSize: 12 }}
                tickFormatter={formatMonthLabel}
              />
              <YAxis tick={{ fill: "rgba(244, 238, 230, 0.72)", fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(15, 19, 18, 0.96)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: "18px",
                  color: "#f4eee6"
                }}
                labelFormatter={(value) => formatMonthLabel(String(value))}
              />
              <ReferenceLine stroke="rgba(255,255,255,0.15)" y={0} />
              {selectedDate ? (
                <ReferenceLine stroke="rgba(207, 158, 88, 0.6)" strokeDasharray="4 4" x={selectedDate} />
              ) : null}
              <Area
                dataKey="grace_twsa_cm"
                fill="url(#twsaFill)"
                name="TWS anomaly"
                stroke="#cf9e58"
                strokeWidth={3}
                type="monotone"
                unit=" cm"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}

export default TimeSeriesChart;
