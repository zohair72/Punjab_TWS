import { useDashboardData } from "../context/DashboardDataContext";

function StatusBanner() {
  const { stats, timeline, loading, refreshing, dashboardError, refreshDashboard } =
    useDashboardData();

  return (
    <section className="mb-6 grid gap-4 lg:grid-cols-[minmax(0,1fr)_auto]">
      <div className="rounded-[24px] border border-white/10 bg-white/5 p-5 backdrop-blur">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">
          System Status
        </p>
        <p className="mt-3 text-base text-cream/90">
          {loading
            ? "Loading dashboard data from the FastAPI backend..."
            : dashboardError
              ? dashboardError
              : `Serving ${timeline.length} stored Punjab-wide monthly records from the backend.`}
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:min-w-[340px]">
        <div className="rounded-[24px] border border-white/10 bg-white/5 p-5 backdrop-blur">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">
            Coverage
          </p>
          <p className="mt-3 text-lg font-medium text-cream">
            {stats ? `${stats.start_date} to ${stats.end_date}` : "Waiting for stats"}
          </p>
        </div>
        <button
          className="rounded-[24px] border border-brass/25 bg-brass/10 p-5 text-left transition hover:-translate-y-0.5 hover:bg-brass/15 disabled:cursor-wait disabled:opacity-60"
          disabled={loading || refreshing}
          onClick={() => void refreshDashboard()}
          type="button"
        >
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">
            Backend Cache
          </p>
          <p className="mt-3 text-lg font-medium text-cream">
            {refreshing ? "Refreshing..." : "Refresh Stored Data"}
          </p>
        </button>
      </div>
    </section>
  );
}

export default StatusBanner;

