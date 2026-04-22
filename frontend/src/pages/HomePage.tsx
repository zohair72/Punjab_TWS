import MapView from "../components/MapView";
import MethodologyPanel from "../components/MethodologyPanel";
import SidebarStats from "../components/SidebarStats";
import StatusBanner from "../components/StatusBanner";
import SummaryCards from "../components/SummaryCards";
import TimelineSlider from "../components/TimelineSlider";
import TimeSeriesChart from "../components/TimeSeriesChart";

function HomePage() {
  return (
    <>
      <StatusBanner />
      <div className="grid gap-6">
        <TimelineSlider />
        <SummaryCards />
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1.55fr)_minmax(320px,0.85fr)]">
          <div className="grid gap-6">
            <TimeSeriesChart />
            <MapView />
          </div>
          <div className="grid gap-6">
            <SidebarStats />
            <MethodologyPanel />
          </div>
        </div>
      </div>
    </>
  );
}

export default HomePage;

