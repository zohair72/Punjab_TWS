import { useDashboardData } from "../context/DashboardDataContext";
import { formatNumber } from "../lib/format";

function SidebarStats() {
  const { stats, loading } = useDashboardData();

  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">Series Stats</p>
      <h2 className="mt-2 text-2xl font-semibold text-cream">GRACE coverage snapshot</h2>

      {loading || !stats ? (
        <p className="mt-6 text-sm text-cream/70">Loading stats...</p>
      ) : (
        <div className="mt-6 grid gap-4">
          {[
            { label: "Coverage start", value: stats.start_date },
            { label: "Coverage end", value: stats.end_date },
            { label: "Series minimum", value: formatNumber(stats.grace_min, { suffix: " cm" }) },
            { label: "Series maximum", value: formatNumber(stats.grace_max, { suffix: " cm" }) },
            { label: "Series mean", value: formatNumber(stats.grace_mean, { suffix: " cm" }) },
            {
              label: "Latest value",
              value: formatNumber(stats.latest_grace_twsa_cm, { suffix: " cm" })
            }
          ].map((item) => (
            <div
              className="rounded-2xl border border-white/10 bg-obsidian/45 px-4 py-3"
              key={item.label}
            >
              <p className="text-xs font-semibold uppercase tracking-[0.25em] text-brass">
                {item.label}
              </p>
              <p className="mt-2 text-lg font-medium text-cream">{item.value}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SidebarStats;

