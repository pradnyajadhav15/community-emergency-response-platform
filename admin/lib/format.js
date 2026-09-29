export const statusColors = {
  OPEN: "#dc2626",
  ACKNOWLEDGED: "#f59e0b",
  IN_PROGRESS: "#2563eb",
  ESCALATED: "#db2777",
  RESOLVED: "#16a34a",
  CLOSED: "#64748b",
  CANCELLED: "#64748b",
};

export const roleLabels = {
  RESIDENT: "Resident",
  GUARDIAN: "Guardian",
  VOLUNTEER: "Volunteer",
  SECURITY: "Security",
  ADMIN: "Administrator",
};

export function when(value) {
  if (!value) return "-";
  return new Date(value).toLocaleString("en-IN", {
    day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

export function duration(seconds) {
  if (seconds == null) return "-";
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
  return `${(seconds / 3600).toFixed(1)}h`;
}