const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
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
  return value;
}

export function formatBinary(value: boolean | null | undefined): string {
  return value ? "Yes" : "No";
}
