import MapView from "../components/MapView";
import MethodologyPanel from "../components/MethodologyPanel";
import TimelineSlider from "../components/TimelineSlider";

function MethodologyPage() {
  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
      <div className="grid gap-6">
        <TimelineSlider />
        <MapView />
      </div>
      <MethodologyPanel />
    </div>
  );
}

export default MethodologyPage;

