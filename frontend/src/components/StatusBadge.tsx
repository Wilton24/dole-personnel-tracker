export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    Available: "badge-available",
    Engaged: "badge-engaged",
    Ongoing: "badge-ongoing",
    Completed: "badge-completed",
  };
  return <span className={`badge ${map[status] || ""}`}>{status}</span>;
}
