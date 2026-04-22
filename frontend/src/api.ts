import axios from "axios";

export type TimelineItem = {
  year: number | null;
  month: number | null;
  date: string;
};

export type MonthlySummaryRecord = {
  date: string;
  year: number | null;
  month: number | null;
  grace_twsa_cm: number | null;
  gldas_precip: number | null;
  gldas_soil_moisture: number | null;
  gldas_et: number | null;
  gldas_air_temp: number | null;
};

export type SummaryStats = {
  row_count: number;
  start_date: string;
  end_date: string;
  grace_min: number | null;
  grace_max: number | null;
  grace_mean: number | null;
  latest_grace_twsa_cm: number | null;
};

export type RefreshResponse = {
  message: string;
  row_count?: number | null;
  metadata_available?: boolean | null;
};

export type MethodologyResponse = {
  project_scope: string;
  primary_signal: string;
  gldas_role: string;
  limitations: string[];
  not_groundwater_measurement: string;
  scale_note: string;
  datasets_used: string[];
};

const browserDefaultApiBaseUrl =
  typeof window !== "undefined"
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : "http://127.0.0.1:8000";

const apiBaseUrl =
  import.meta.env.API_BASE_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  browserDefaultApiBaseUrl;

const apiClient = axios.create({
  baseURL: apiBaseUrl,
  timeout: 15000
});

export async function fetchTimeline() {
  const response = await apiClient.get<TimelineItem[]>("/api/timeline");
  return response.data;
}

export async function fetchLatestSummary() {
  const response = await apiClient.get<MonthlySummaryRecord>("/api/summary/latest");
  return response.data;
}

export async function fetchTimeseries() {
  const response = await apiClient.get<MonthlySummaryRecord[]>("/api/summary/timeseries");
  return response.data;
}

export async function fetchSummaryByDate(year: number, month: number) {
  const response = await apiClient.get<MonthlySummaryRecord>("/api/summary/by-date", {
    params: { year, month }
  });
  return response.data;
}

export async function fetchSummaryStats() {
  const response = await apiClient.get<SummaryStats>("/api/summary/stats");
  return response.data;
}

export async function refreshSummaryCache() {
  const response = await apiClient.get<RefreshResponse>("/api/summary/refresh");
  return response.data;
}

export async function fetchMethodology() {
  const response = await apiClient.get<MethodologyResponse>("/api/methodology");
  return response.data;
}
