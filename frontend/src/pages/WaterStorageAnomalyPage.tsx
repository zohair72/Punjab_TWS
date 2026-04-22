const conceptCards = [
  {
    eyebrow: "TWSA",
    title: "Terrestrial Water Storage Anomaly",
    description:
      "TWSA measures how much total stored water differs from its long-term average. It combines groundwater, soil moisture, surface water, and other stored water components into one regional signal.",
    highlights: [
      "Positive anomaly: more stored water than the long-term average.",
      "Negative anomaly: less stored water than the long-term average.",
      "Why it matters: useful for tracking regional stress, recovery, and drought conditions."
    ]
  },
  {
    eyebrow: "Precipitation",
    title: "Precipitation",
    description:
      "Precipitation is the amount of rain or snow falling over a period of time. In this dashboard it is shown as same-month GLDAS context to help interpret whether Punjab is receiving relatively low or high moisture inputs.",
    highlights: [
      "Higher precipitation usually means more water entering the regional system.",
      "This can support reservoirs, soil moisture, and groundwater recharge conditions.",
      "Precipitation is context here, not the main scientific signal."
    ]
  },
  {
    eyebrow: "Soil Moisture",
    title: "Soil Moisture",
    description:
      "Soil moisture reflects how much water is retained in the soil. It is important for crop health, vegetation, and land-atmosphere interactions and helps explain whether surface conditions are dry or wet in a selected month.",
    highlights: [
      "Higher soil moisture generally supports agriculture and vegetation.",
      "Lower soil moisture can indicate emerging dryness or stress.",
      "Like precipitation, this is contextual support data alongside GRACE."
    ]
  }
];

function WaterStorageAnomalyPage() {
  return (
    <div className="grid gap-6">
      <section className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">
          Water Storage Concepts
        </p>
        <h2 className="mt-2 text-3xl font-semibold text-cream">
          How to read the dashboard metrics
        </h2>
        <p className="mt-3 max-w-4xl text-sm leading-7 text-cream/75">
          This page explains the main regional concepts shown in the Punjab Groundwater
          Stress Dashboard. The core signal is Punjab-wide terrestrial water storage anomaly
          from GRACE/GRACE-FO, while precipitation and soil moisture are supporting context
          variables used to interpret the selected month.
        </p>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        {conceptCards.map((card) => (
          <article
            className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur"
            key={card.title}
          >
            <div className="inline-flex rounded-full border border-brass/20 bg-brass/10 px-3 py-2 text-xs font-semibold uppercase tracking-[0.3em] text-brass">
              {card.eyebrow}
            </div>
            <h3 className="mt-5 text-2xl font-semibold text-cream">{card.title}</h3>
            <p className="mt-4 text-sm leading-7 text-cream/75">{card.description}</p>
            <ul className="mt-5 space-y-3">
              {card.highlights.map((item) => (
                <li
                  className="rounded-2xl border border-white/10 bg-obsidian/45 px-4 py-3 text-sm leading-6 text-cream/75"
                  key={item}
                >
                  {item}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </section>

      <section className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">
          Interpreting the Map
        </p>
        <h3 className="mt-2 text-2xl font-semibold text-cream">Regional color logic</h3>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          {[
            {
              title: "Green",
              body: "Represents wetter or more favorable regional conditions. For TWSA, this means positive anomaly. For precipitation and soil moisture, it means relatively higher conditions within the Punjab record.",
              swatch: "bg-emerald-500"
            },
            {
              title: "Yellow",
              body: "Represents moderate or near-average regional conditions. It is useful as a middle category between clear wet and clear dry signals.",
              swatch: "bg-amber-400"
            },
            {
              title: "Red",
              body: "Represents drier or more stressed conditions. For TWSA, this means negative anomaly. For precipitation and soil moisture, it means relatively lower conditions in the historical Punjab series.",
              swatch: "bg-rose-500"
            }
          ].map((item) => (
            <div
              className="rounded-[24px] border border-white/10 bg-obsidian/45 p-5"
              key={item.title}
            >
              <div className="flex items-center gap-3">
                <span className={`h-4 w-4 rounded-full ${item.swatch}`} />
                <h4 className="text-lg font-medium text-cream">{item.title}</h4>
              </div>
              <p className="mt-4 text-sm leading-7 text-cream/75">{item.body}</p>
            </div>
          ))}
        </div>
        <p className="mt-6 text-sm leading-7 text-cream/65">
          The map is still province-scale. Color is spread across the full Punjab boundary
          to represent a Punjab-wide monthly condition, not sub-district variation.
        </p>
      </section>
    </div>
  );
}

export default WaterStorageAnomalyPage;
