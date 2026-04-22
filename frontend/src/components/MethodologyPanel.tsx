import { useDashboardData } from "../context/DashboardDataContext";

function MethodologyPanel() {
  const { methodology, loading, dashboardError } = useDashboardData();

  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">
        Methodology
      </p>
      <h2 className="mt-2 text-2xl font-semibold text-cream">Scientific framing and limits</h2>

      <div className="mt-6 space-y-4 text-sm leading-7 text-cream/75">
        {loading ? <p>Loading methodology details...</p> : null}
        {!loading && dashboardError && !methodology ? <p className="text-rose-200">{dashboardError}</p> : null}
        {!loading && methodology ? (
          <>
            <p>{methodology.project_scope}</p>
            <p>{methodology.primary_signal}</p>
            <p>{methodology.gldas_role}</p>
            <p>{methodology.not_groundwater_measurement}</p>
            <p>{methodology.scale_note}</p>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">Limitations</p>
              <ul className="mt-3 space-y-2">
                {methodology.limitations.map((item) => (
                  <li className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3" key={item}>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">Datasets</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {methodology.datasets_used.map((dataset) => (
                  <span
                    className="rounded-full border border-brass/20 bg-brass/10 px-3 py-2 text-xs text-brass"
                    key={dataset}
                  >
                    {dataset}
                  </span>
                ))}
              </div>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}

export default MethodologyPanel;

