const currency = new Intl.NumberFormat("en-CA", {
  style: "currency",
  currency: "CAD",
  maximumFractionDigits: 0
});

export function formatCurrency(value: number | null | undefined): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "$0";
  }
  return currency.format(value);
}

export function formatRating(value: number | null | undefined): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "—";
  }
  return value.toFixed(1);
}

export function formatNumber(value: number | null | undefined): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "0";
  }
  return value.toLocaleString("en-US");
}

export function formatDate(value: string): string {
  if (!value) {
    return "Unknown date";
  }
  return value.length > 10 ? value.slice(0, 10) : value;
}

export function formatBinary(value: boolean | null | undefined): string {
  return value ? "Yes" : "No";
}

export function formatAdultOnly(value: number | null | undefined): string {
  if (value === null || value === undefined) return "—";
  const numeric = value;
  if (Number.isNaN(numeric)) return "—";
  if (numeric === 0) return "No";
  if (numeric === 1) return "Yes";
  return "Maybe";
}
