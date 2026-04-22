import { useDashboardData } from "../context/DashboardDataContext";
import { formatCompact, formatMonthLabel, formatNumber } from "../lib/format";

function SummaryCards() {
  const { selectedRecord, stats, loading, dashboardError, selectionError } = useDashboardData();

  if (loading) {
    return (
      <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
        <p className="text-sm text-cream/70">Loading summary cards...</p>
      </div>
    );
  }

  if (!selectedRecord) {
    return (
      <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
        <p className="text-sm text-rose-200">
          {selectionError ?? dashboardError ?? "No summary record is available."}
        </p>
      </div>
    );
  }

  const cards = [
    {
      title: "Punjab TWS anomaly",
      value: formatNumber(selectedRecord.grace_twsa_cm, { suffix: " cm" }),
      accent: "from-brass/25 to-brass/5",
      helper: "GRACE/GRACE-FO terrestrial water storage anomaly for the selected month."
    },
    {
      title: "GLDAS precipitation",
      value: formatCompact(selectedRecord.gldas_precip),
      accent: "from-sky-400/20 to-sky-300/5",
      helper: "Same-month contextual precipitation support value."
    },
    {
      title: "GLDAS soil moisture",
      value: formatCompact(selectedRecord.gldas_soil_moisture),
      accent: "from-emerald-400/20 to-emerald-300/5",
      helper: "Punjab-scale hydrologic state context from GLDAS."
    },
    {
      title: "GLDAS ET",
      value: formatCompact(selectedRecord.gldas_et),
      accent: "from-amber-300/20 to-amber-100/5",
      helper: "Monthly evapotranspiration or documented proxy from GLDAS."
    },
    {
      title: "GLDAS air temperature",
      value: formatNumber(selectedRecord.gldas_air_temp, { suffix: " deg C" }),
      accent: "from-rose-400/20 to-rose-200/5",
      helper: "Monthly mean air temperature context."
    },
    {
      title: "Stored coverage",
      value: stats ? `${stats.row_count} months` : formatMonthLabel(selectedRecord.date),
      accent: "from-white/10 to-white/5",
      helper: `Selected snapshot: ${formatMonthLabel(selectedRecord.date)}.`
    }
  ];

  return (
    <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {cards.map((card) => (
        <article
          className={`group rounded-[28px] border border-white/10 bg-gradient-to-br ${card.accent} p-[1px] shadow-glow`}
          key={card.title}
        >
          <div className="h-full rounded-[27px] bg-obsidian/90 p-5 transition duration-200 group-hover:bg-obsidian/85">
            <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">
              {card.title}
            </p>
            <p className="mt-4 text-3xl font-semibold tracking-tight text-cream">
              {card.value}
            </p>
            <p className="mt-4 text-sm leading-6 text-cream/70">{card.helper}</p>
          </div>
        </article>
      ))}
    </section>
  );
}

export default SummaryCards;
