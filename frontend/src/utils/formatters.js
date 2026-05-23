export function shortAddress(address, start = 6, end = 6) {
  if (!address || typeof address !== "string") return "Not available";
  if (address.length <= start + end) return address;
  return `${address.slice(0, start)}...${address.slice(-end)}`;
}

export function formatNumber(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) return "Not available";

  return number.toLocaleString(undefined, {
    maximumFractionDigits: 4,
  });
}

export function formatPercent(value) {
  const number = Number(value);

  if (!Number.isFinite(number)) return "0%";

  return `${number.toFixed(2)}%`;
}

export async function copyToClipboard(text) {
  if (!text) return false;

  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    return false;
  }
}