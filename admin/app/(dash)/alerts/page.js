"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import { apiError } from "@/lib/api";
import { fetchAll } from "@/lib/fetchAll";
import { statusColors, when } from "@/lib/format";

const ACTIVE = ["OPEN", "ACKNOWLEDGED", "IN_PROGRESS", "ESCALATED"];
const FILTERS = ["ACTIVE", "ALL", "OPEN", "IN_PROGRESS", "ESCALATED", "RESOLVED", "CLOSED"];

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState("ACTIVE");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      setAlerts(await fetchAll("/sos/"));
      setError("");
    } catch (e) {
      setError(apiError(e, "Could not load alerts."));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    const t = setInterval(load, 15000);
    return () => clearInterval(t);
  }, []);

  const shown = useMemo(() => {
    if (filter === "ALL") return alerts;
    if (filter === "ACTIVE") return alerts.filter((a) => ACTIVE.includes(a.status));
    return alerts.filter((a) => a.status === filter);
  }, [alerts, filter]);

  return (
    <>
      <h1 className="page-title">Alerts</h1>
      <p className="page-sub">Every SOS raised in the network. Refreshes every 15 seconds.</p>

      {error && <div className="banner banner-error">{error}</div>}

      <div className="chips">
        {FILTERS.map((f) => (
          <button
            key={f}
            className={`btn btn-sm ${filter === f ? "" : "btn-ghost"}`}
            onClick={() => setFilter(f)}
          >
            {f.replace("_", " ")}
          </button>
        ))}
      </div>

      <div className="card">
        {loading ? (
          <div className="empty">Loading...</div>
        ) : shown.length === 0 ? (
          <div className="empty">No alerts match this filter.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Category</th><th>Resident</th><th>Location</th>
                <th>Tier</th><th>Responder</th><th>Raised</th><th>Status</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((a) => (
                <tr key={a.id}>
                  <td><Link href={`/alerts/${a.id}`} style={{ color: "var(--primary)" }}>#{a.id}</Link></td>
                  <td>{a.category_display}</td>
                  <td>{a.resident_name}</td>
                  <td className="muted small">{a.flat_label || "-"}</td>
                  <td>{a.escalation_level}</td>
                  <td>{a.responder_name || <span className="muted">unclaimed</span>}</td>
                  <td className="muted small">{when(a.created_at)}</td>
                  <td>
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
    </>
  );
}