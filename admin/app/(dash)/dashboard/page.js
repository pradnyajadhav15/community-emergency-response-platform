"use client";

import { useEffect, useState } from "react";

import api, { apiError } from "@/lib/api";
import { duration, statusColors, when } from "@/lib/format";

function Stat({ label, value, note, color }) {
  return (
    <div className="card">
      <div className="stat-label">{label}</div>
      <div className="stat-value" style={color ? { color } : undefined}>{value}</div>
      {note && <div className="stat-note">{note}</div>}
    </div>
  );
}

function Bars({ rows, keyName }) {
  const max = Math.max(1, ...rows.map((r) => r.count));
  if (rows.length === 0) return <div className="empty">No data yet.</div>;
  return rows.map((r) => (
    <div className="bar-row" key={r[keyName]}>
      <div className="bar-label">{r[keyName]}</div>
      <div className="bar-track">
        <div
          className="bar-fill"
          style={{
            width: `${(r.count / max) * 100}%`,
            background: keyName === "status" ? statusColors[r.status] : undefined,
          }}
        />
      </div>
      <div className="bar-count">{r.count}</div>
    </div>
  ));
}

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recent, setRecent] = useState([]);
  const [error, setError] = useState("");

  async function load() {
    try {
      const [s, a] = await Promise.all([
        api.get("/dashboard/stats/"),
        api.get("/sos/"),
      ]);
      setStats(s.data);
      setRecent((a.data.results || a.data).slice(0, 6));
      setError("");
    } catch (e) {
      setError(apiError(e, "Could not load dashboard data."));
    }
  }

  useEffect(() => {
    load();
    const timer = setInterval(load, 15000);
    return () => clearInterval(timer);
  }, []);

  const delivery = stats?.notifications;
  const rate = delivery?.total
    ? Math.round((delivery.sent / delivery.total) * 100)
    : 0;

  return (
    <>
      <h1 className="page-title">Dashboard</h1>
      <p className="page-sub">Live overview, refreshed every 15 seconds.</p>

      {error && <div className="banner banner-error">{error}</div>}
      {!stats && !error && <div className="empty">Loading...</div>}

      {stats && (
        <>
          <div className="grid grid-4 mb">
            <Stat label="Total Alerts" value={stats.total_alerts} />
            <Stat
              label="Active Now"
              value={stats.active_alerts}
              color={stats.active_alerts > 0 ? "var(--danger)" : undefined}
              note={stats.active_alerts > 0 ? "Requires attention" : "All clear"}
            />
            <Stat label="Resolved" value={stats.resolved_alerts} color="var(--success)" />
            <Stat
              label="Avg Resolution"
              value={duration(stats.avg_resolution_seconds)}
              note={`${stats.escalated_alerts} escalated`}
            />
          </div>

          <div className="grid grid-2 mb">
            <div className="card">
              <div className="card-title">Alerts by Category</div>
              <Bars rows={stats.by_category} keyName="category" />
            </div>
            <div className="card">
              <div className="card-title">Alerts by Status</div>
              <Bars rows={stats.by_status} keyName="status" />
            </div>
          </div>

          <div className="grid grid-2">
            <div className="card">
              <div className="card-title">Notification Delivery</div>
              <div className="between mb">
                <span className="muted small">Success rate</span>
                <strong style={{ color: rate > 80 ? "var(--success)" : "var(--warning)" }}>
                  {rate}%
                </strong>
              </div>
              <div className="bar-track mb">
                <div className="bar-fill" style={{ width: `${rate}%`, background: "var(--success)" }} />
              </div>
              <div className="between small muted">
                <span>Sent: {delivery?.sent ?? 0}</span>
                <span>Failed: {delivery?.failed ?? 0}</span>
                <span>Total: {delivery?.total ?? 0}</span>
              </div>
            </div>

            <div className="card">
              <div className="card-title">Recent Alerts</div>
              {recent.length === 0 ? (
                <div className="empty">No alerts yet.</div>
              ) : (
                <table>
                  <tbody>
                    {recent.map((a) => (
                      <tr key={a.id}>
                        <td style={{ width: 40 }} className="muted">#{a.id}</td>
                        <td>{a.category_display}</td>
                        <td className="muted small">{when(a.created_at)}</td>
                        <td style={{ textAlign: "right" }}>
                          <span className="badge" style={{ background: statusColors[a.status] }}>
                            {a.status_display}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </>
      )}
    </>
  );
}