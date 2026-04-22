import { NavLink, Navigate, Route, Routes } from "react-router-dom";

import { DashboardDataProvider } from "./context/DashboardDataContext";
import HomePage from "./pages/HomePage";
import MethodologyPage from "./pages/MethodologyPage";
import TimeseriesPage from "./pages/TimeseriesPage";
import WaterStorageAnomalyPage from "./pages/WaterStorageAnomalyPage";

const navItems = [
  { label: "Overview", to: "/" },
  { label: "Time Series", to: "/timeseries" },
  { label: "Concepts", to: "/water-storage-anomaly" },
  { label: "Methodology", to: "/methodology" }
];

function App() {
  return (
    <DashboardDataProvider>
      <div className="min-h-screen bg-dashboard-radial text-cream">
        <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 pb-10 pt-6 sm:px-6 lg:px-8">
          <header className="mb-6 rounded-[28px] border border-white/10 bg-white/5 p-5 shadow-glow backdrop-blur">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
              <div className="max-w-3xl">
                <p className="mb-2 text-xs font-semibold uppercase tracking-[0.35em] text-brass">
                  Punjab Scale Water Storage Visualization
                </p>
                <h1 className="text-4xl font-semibold tracking-tight text-cream sm:text-5xl">
                  Punjab Groundwater Stress Dashboard
                </h1>
                <p className="mt-3 max-w-2xl text-sm leading-6 text-cream/75 sm:text-base">
                  A regional dashboard for Punjab-wide terrestrial water storage anomaly
                  from GRACE/GRACE-FO, paired with same-month GLDAS context and served
                  from stored processed outputs.
                </p>
              </div>
              <div className="grid gap-2 sm:grid-cols-3">
                {["GRACE-paced sync", "Stored outputs", "No district analytics"].map((tag) => (
                  <span
                    className="rounded-full border border-brass/25 bg-brass/10 px-4 py-2 text-center text-sm text-brass"
                    key={tag}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
            <nav className="mt-6 flex flex-wrap gap-3">
              {navItems.map((item) => (
                <NavLink
                  className={({ isActive }) =>
                    [
                      "rounded-full px-4 py-2 text-sm transition",
                      isActive
                        ? "bg-cream text-obsidian"
                        : "border border-white/10 bg-white/5 text-cream/80 hover:bg-white/10"
                    ].join(" ")
                  }
                  end={item.to === "/"}
                  key={item.to}
                  to={item.to}
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </header>

          <Routes>
            <Route element={<HomePage />} path="/" />
            <Route element={<TimeseriesPage />} path="/timeseries" />
            <Route element={<WaterStorageAnomalyPage />} path="/water-storage-anomaly" />
            <Route element={<MethodologyPage />} path="/methodology" />
            <Route element={<Navigate replace to="/" />} path="*" />
          </Routes>
        </div>
      </div>
    </DashboardDataProvider>
  );
}

export default App;
