export function formatMonthLabel(date: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    year: "numeric"
  }).format(new Date(date));
}

export function formatNumber(
  value: number | null,
  options?: { digits?: number; suffix?: string }
) {
  if (value == null || Number.isNaN(value)) {
    return "Not available";
  }

  const digits = options?.digits ?? 2;
  const suffix = options?.suffix ?? "";
  return `${value.toFixed(digits)}${suffix}`;
}

export function formatCompact(value: number | null) {
  if (value == null || Number.isNaN(value)) {
    return "Not available";
  }

  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1
  }).format(value);
}

