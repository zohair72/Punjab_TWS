import { useDashboardData } from "../context/DashboardDataContext";
import { formatMonthLabel } from "../lib/format";

function TimelineSlider() {
  const { timeline, selectedDate, setSelectedDate, loading } = useDashboardData();

  const selectedIndex = Math.max(
    0,
    timeline.findIndex((item) => item.date === selectedDate)
  );

  const activeDate = selectedDate ?? timeline[timeline.length - 1]?.date;

  return (
    <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-brass">
            Interactive Timeline
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-cream">Choose a Punjab monthly snapshot</h2>
          <p className="mt-2 text-sm text-cream/70">
            Timeline selection drives the summary cards and map tooltip for the chosen month.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-[minmax(0,260px)_auto] sm:items-end">
          <label className="grid gap-2 text-sm text-cream/80">
            <span className="text-xs font-semibold uppercase tracking-[0.25em] text-brass">
              Available month
            </span>
            <select
              className="rounded-2xl border border-white/10 bg-obsidian/60 px-4 py-3 text-cream outline-none transition focus:border-brass/60"
              disabled={loading || timeline.length === 0}
              onChange={(event) => setSelectedDate(event.target.value)}
              value={activeDate ?? ""}
            >
              {timeline.map((item) => (
                <option key={item.date} value={item.date}>
                  {formatMonthLabel(item.date)}
                </option>
              ))}
            </select>
          </label>
          <div className="rounded-2xl border border-white/10 bg-obsidian/45 px-4 py-3">
            <p className="text-xs font-semibold uppercase tracking-[0.25em] text-brass">Selected</p>
            <p className="mt-2 text-lg font-medium text-cream">
              {activeDate ? formatMonthLabel(activeDate) : "No data"}
            </p>
          </div>
        </div>
      </div>

      <div className="mt-6">
        {loading ? (
          <p className="rounded-2xl bg-white/5 px-4 py-3 text-sm text-cream/70">
            Loading available months...
          </p>
        ) : timeline.length === 0 ? (
          <p className="rounded-2xl bg-white/5 px-4 py-3 text-sm text-cream/70">
            No processed months are available yet.
          </p>
        ) : (
          <>
            <input
              className="timeline-range h-2 w-full cursor-pointer appearance-none rounded-full bg-white/10"
              max={timeline.length - 1}
              min={0}
              onChange={(event) => setSelectedDate(timeline[Number(event.target.value)].date)}
              step={1}
              type="range"
              value={selectedIndex}
            />
            <div className="mt-3 flex justify-between text-xs uppercase tracking-[0.22em] text-cream/50">
              <span>{formatMonthLabel(timeline[0].date)}</span>
              <span>{formatMonthLabel(timeline[timeline.length - 1].date)}</span>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default TimelineSlider;

