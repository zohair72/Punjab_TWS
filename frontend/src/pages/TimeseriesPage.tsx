import SidebarStats from "../components/SidebarStats";
import TimelineSlider from "../components/TimelineSlider";
import TimeSeriesChart from "../components/TimeSeriesChart";

function TimeseriesPage() {
  return (
    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.6fr)_minmax(320px,0.8fr)]">
      <div className="grid gap-6">
        <TimelineSlider />
        <TimeSeriesChart />
      </div>
      <SidebarStats />
    </div>
  );
}

export default TimeseriesPage;

