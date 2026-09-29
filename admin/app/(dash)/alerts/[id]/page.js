"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import api, { apiError } from "@/lib/api";
import { statusColors, when } from "@/lib/format";

const deliveryColors = {
  SENT: "#16a34a", FAILED: "#dc2626", READ: "#2563eb", PENDING: "#f59e0b",
};

function Row({ label, value }) {
  return (
    <div className="detail-row">
      <span className="muted">{label}</span>
      <span>{value || "-"}</span>
    </div>
  );
}

export default function AlertDetail() {
  const { id } = useParams();
  const [alert, setAlert] = useState(null);
  const [log, setLog] = useState([]);
  const [messages, setMessages] = useState([]);
  const [notes, setNotes] = useState("");
  const [draft, setDraft] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      const [a, n, m] = await Promise.all([
        api.get(`/sos/${id}/`),
        api.get(`/sos/${id}/notifications/`),
        api.get(`/incidents/messages/?alert=${id}`),
      ]);
      setAlert(a.data);
      setLog(n.data);
      setMessages(m.data.results || m.data);
      setError("");
    } catch (e) {
      setError(apiError(e, "Could not load this alert."));
    }
  }, [id]);

  useEffect(() => {
    load();
    const t = setInterval(load, 10000);
    return () => clearInterval(t);
  }, [load]);

  async function act(path, body) {
    setBusy(true);
    try {
      await api.post(`/sos/${id}/${path}/`, body || {});
      await load();
    } catch (e) {
      setError(apiError(e, "Action failed."));
    } finally {
      setBusy(false);
    }
  }

  async function send(e) {
    e.preventDefault();
    if (!draft.trim()) return;
    try {
      await api.post("/incidents/messages/", { alert: Number(id), body: draft.trim() });
      setDraft("");
      await load();
    } catch (err) {
      setError(apiError(err, "Message not sent."));
    }
  }

  if (!alert) {
    return error ? <div className="banner banner-error">{error}</div> : <div className="empty">Loading...</div>;
  }

  const isOpen = !["RESOLVED", "CLOSED", "CANCELLED"].includes(alert.status);

  return (
    <>
      <Link href="/alerts" className="back">&larr; All alerts</Link>
      <div className="between">
        <h1 className="page-title">{alert.category_display} &middot; #{alert.id}</h1>
        <span className="badge" style={{ background: statusColors[alert.status], fontSize: 13 }}>
          {alert.status_display}
        </span>
      </div>
      <p className="page-sub">{alert.message || "No message provided."}</p>

      {error && <div className="banner banner-error">{error}</div>}

      <div className="grid grid-2 mb">
        <div className="card">
          <div className="card-title">Details</div>
          <Row label="Resident" value={alert.resident_name} />
          <Row label="Phone" value={alert.resident_phone} />
          <Row label="Location" value={alert.flat_label} />
          <Row
            label="GPS"
            value={
              alert.latitude != null ? (
                <a
                  href={`https://maps.google.com/?q=${alert.latitude},${alert.longitude}`}
                  target="_blank"
                  rel="noreferrer"
                  style={{ color: "var(--primary)" }}
                >
                  {alert.latitude.toFixed(5)}, {alert.longitude.toFixed(5)}
                </a>
              ) : null
            }
          />
          <Row label="Escalation tier" value={`${alert.escalation_level} of 3`} />
          <Row label="Responder" value={alert.responder_name} />
          <Row label="Raised" value={when(alert.created_at)} />
          <Row label="Acknowledged" value={when(alert.acknowledged_at)} />
          <Row label="Escalated" value={when(alert.escalated_at)} />
          <Row label="Resolved" value={when(alert.resolved_at)} />
          <Row label="Closed" value={when(alert.closed_at)} />
          {alert.resolution_notes && <Row label="Resolution" value={alert.resolution_notes} />}
        </div>

        <div className="card">
          <div className="card-title">Actions</div>
          {!isOpen && alert.status !== "CLOSED" && (
            <button className="btn" disabled={busy} onClick={() => act("close")}>Close Incident</button>
          )}
          {!isOpen && alert.status === "CLOSED" && (
            <div className="muted small">This incident is closed.</div>
          )}
          {isOpen && (
            <>
              <div className="row mb">
                <button className="btn btn-ghost" disabled={busy || !!alert.acknowledged_at} onClick={() => act("acknowledge")}>
                  Acknowledge
                </button>
                <button className="btn btn-ghost" disabled={busy || alert.escalation_level >= 3} onClick={() => act("escalate")}>
                  Escalate to Tier {Math.min(alert.escalation_level + 1, 3)}
                </button>
              </div>
              <div className="field">
                <label>Resolution notes</label>
                <input value={notes} onChange={(e) => setNotes(e.target.value)} placeholder="What happened and how it was handled" />
              </div>
              <button
                className="btn btn-danger"
                disabled={busy}
                onClick={() => act("resolve", { resolution_notes: notes || "Resolved by administrator." })}
              >
                Mark Resolved
              </button>
            </>
          )}
        </div>
      </div>

      <div className="card mb">
        <div className="card-title">Notification Log ({log.length})</div>
        {log.length === 0 ? (
          <div className="empty">No notifications recorded.</div>
        ) : (
          <table>
            <thead>
              <tr><th>Recipient</th><th>Audience</th><th>Channel</th><th>Status</th><th>Detail</th><th>Sent</th></tr>
            </thead>
            <tbody>
              {log.map((n) => (
                <tr key={n.id}>
                  <td>{n.recipient_label}</td>
                  <td className="muted small">{n.audience_display}</td>
                  <td>{n.channel}</td>
                  <td>
                    <span className="badge" style={{ background: deliveryColors[n.status] }}>{n.status}</span>
                  </td>
                  <td className="muted small" style={{ maxWidth: 260, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {n.status === "FAILED" ? n.error : ""}
                  </td>
                  <td className="muted small">{when(n.sent_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <div className="card-title">Incident Thread</div>
        {messages.length === 0 && <div className="empty">No messages yet.</div>}
        {messages.map((m) => (
          <div key={m.id} className={`msg ${m.is_system ? "system" : ""}`}>
            {!m.is_system && (
              <div className="small muted" style={{ marginBottom: 4 }}>
                <strong style={{ color: "var(--text)" }}>{m.sender_name}</strong> &middot; {m.sender_role} &middot; {when(m.created_at)}
              </div>
            )}
            <div>{m.body}</div>
          </div>
        ))}
        <form onSubmit={send} className="row mt">
          <div className="field" style={{ flex: 1, marginBottom: 0 }}>
            <input value={draft} onChange={(e) => setDraft(e.target.value)} placeholder="Message responders and the resident" />
          </div>
          <button className="btn">Send</button>
        </form>
      </div>
    </>
  );
}