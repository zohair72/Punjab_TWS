import axios from "axios";
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type PropsWithChildren
} from "react";

import {
  fetchLatestSummary,
  fetchMethodology,
  fetchSummaryByDate,
  fetchSummaryStats,
  fetchTimeline,
  fetchTimeseries,
  refreshSummaryCache,
  waitForBackendWakeup,
  type MethodologyResponse,
  type MonthlySummaryRecord,
  type SummaryStats,
  type TimelineItem
} from "../api";

type DashboardContextValue = {
  timeline: TimelineItem[];
  timeseries: MonthlySummaryRecord[];
  latestRecord: MonthlySummaryRecord | null;
  selectedRecord: MonthlySummaryRecord | null;
  methodology: MethodologyResponse | null;
  stats: SummaryStats | null;
  selectedDate: string | null;
  loading: boolean;
  refreshing: boolean;
  dashboardError: string | null;
  selectionError: string | null;
  setSelectedDate: (date: string) => void;
  refreshDashboard: () => Promise<void>;
};

const DashboardDataContext = createContext<DashboardContextValue | undefined>(undefined);

function formatApiError(error: unknown) {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    return typeof detail === "string" ? detail : error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "An unexpected error occurred while loading dashboard data.";
}

export function DashboardDataProvider({ children }: PropsWithChildren) {
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [timeseries, setTimeseries] = useState<MonthlySummaryRecord[]>([]);
  const [latestRecord, setLatestRecord] = useState<MonthlySummaryRecord | null>(null);
  const [selectedRecord, setSelectedRecord] = useState<MonthlySummaryRecord | null>(null);
  const [methodology, setMethodology] = useState<MethodologyResponse | null>(null);
  const [stats, setStats] = useState<SummaryStats | null>(null);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [dashboardError, setDashboardError] = useState<string | null>(null);
  const [selectionError, setSelectionError] = useState<string | null>(null);

  async function loadDashboardData() {
    setLoading(true);
    setDashboardError(null);

    try {
      await waitForBackendWakeup();

      const [timelineData, latestData, timeseriesData, methodologyData, statsData] =
        await Promise.all([
          fetchTimeline(),
          fetchLatestSummary(),
          fetchTimeseries(),
          fetchMethodology(),
          fetchSummaryStats()
        ]);

      setTimeline(timelineData);
      setLatestRecord(latestData);
      setSelectedRecord((current) => current ?? latestData);
      setTimeseries(timeseriesData);
      setMethodology(methodologyData);
      setStats(statsData);
      setSelectedDate((current) => current ?? latestData.date);
      setSelectionError(null);
    } catch (error) {
      setDashboardError(formatApiError(error));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadDashboardData();
  }, []);

  useEffect(() => {
    if (!selectedDate || !latestRecord) {
      return;
    }

    if (selectedDate === latestRecord.date) {
      setSelectedRecord(latestRecord);
      setSelectionError(null);
      return;
    }

    const activeItem = timeline.find((item) => item.date === selectedDate);
    if (activeItem?.year == null || activeItem?.month == null) {
      setSelectionError("Selected month is incomplete.");
      return;
    }

    const selectedYear = activeItem.year;
    const selectedMonth = activeItem.month;
    let cancelled = false;

    async function loadSelectedRecord() {
      try {
        const record = await fetchSummaryByDate(selectedYear, selectedMonth);
        if (!cancelled) {
          setSelectedRecord(record);
          setSelectionError(null);
        }
      } catch (error) {
        if (!cancelled) {
          setSelectionError(formatApiError(error));
        }
      }
    }

    void loadSelectedRecord();
    return () => {
      cancelled = true;
    };
  }, [latestRecord, selectedDate, timeline]);

  async function refreshDashboard() {
    setRefreshing(true);
    setDashboardError(null);

    try {
      await refreshSummaryCache();
      setSelectedRecord(null);
      setSelectedDate(null);
      await loadDashboardData();
    } catch (error) {
      setDashboardError(formatApiError(error));
    } finally {
      setRefreshing(false);
    }
  }

  const value = useMemo<DashboardContextValue>(
    () => ({
      timeline,
      timeseries,
      latestRecord,
      selectedRecord,
      methodology,
      stats,
      selectedDate,
      loading,
      refreshing,
      dashboardError,
      selectionError,
      setSelectedDate,
      refreshDashboard
    }),
    [
      timeline,
      timeseries,
      latestRecord,
      selectedRecord,
      methodology,
      stats,
      selectedDate,
      loading,
      refreshing,
      dashboardError,
      selectionError
    ]
  );

  return <DashboardDataContext.Provider value={value}>{children}</DashboardDataContext.Provider>;
}

export function useDashboardData() {
  const context = useContext(DashboardDataContext);
  if (!context) {
    throw new Error("useDashboardData must be used within DashboardDataProvider.");
  }
  return context;
}
