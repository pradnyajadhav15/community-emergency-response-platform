"use client";

import { useEffect, useMemo, useState } from "react";

import api, { apiError } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { fetchAll } from "@/lib/fetchAll";
import { roleLabels, when } from "@/lib/format";

const ROLES = ["RESIDENT", "GUARDIAN", "VOLUNTEER", "SECURITY", "ADMIN"];

export default function Users() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState([]);
  const [societies, setSocieties] = useState([]);
  const [role, setRole] = useState("ALL");
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function load() {
    try {
      const [u, s] = await Promise.all([fetchAll("/auth/users/"), fetchAll("/societies/")]);
      setUsers(u);
      setSocieties(s);
      setError("");
    } catch (e) {
      setError(apiError(e, "Could not load users."));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function update(id, patch) {
    setError("");
    try {
      const { data } = await api.patch(`/auth/users/${id}/`, patch);
      setUsers((list) => list.map((u) => (u.id === id ? data : u)));
    } catch (e) {
      setError(apiError(e, "Update failed."));
    }
  }

  const counts = useMemo(() => {
    const c = Object.fromEntries(ROLES.map((r) => [r, 0]));
    users.forEach((u) => { c[u.role] = (c[u.role] || 0) + 1; });
    return c;
  }, [users]);

  const shown = users.filter((u) => {
    if (role !== "ALL" && u.role !== role) return false;
    const q = search.trim().toLowerCase();
    if (!q) return true;
    return [u.username, u.first_name, u.email, u.phone].some((v) => (v || "").toLowerCase().includes(q));
  });

  return (
    <>
      <h1 className="page-title">Users</h1>
      <p className="page-sub">Assign roles and societies, and activate or deactivate accounts.</p>

      {error && <div className="banner banner-error">{error}</div>}

      <div className="grid grid-4 mb">
        {ROLES.map((r) => (
          <div className="card" key={r}>
            <div className="stat-label">{roleLabels[r]}</div>
            <div className="stat-value" style={{ fontSize: 26 }}>{counts[r]}</div>
          </div>
        ))}
      </div>

      <div className="between mb">
        <div className="chips" style={{ marginBottom: 0 }}>
          {["ALL", ...ROLES].map((r) => (
            <button key={r} className={`btn btn-sm ${role === r ? "" : "btn-ghost"}`} onClick={() => setRole(r)}>
              {r === "ALL" ? "All" : roleLabels[r]}
            </button>
          ))}
        </div>
        <input
          className="inline-select"
          style={{ width: 240, padding: "8px 12px" }}
          placeholder="Search name, email, phone"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="card">
        {loading ? (
          <div className="empty">Loading...</div>
        ) : shown.length === 0 ? (
          <div className="empty">No users match.</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>User</th><th>Role</th><th>Society</th><th>Phone</th>
                <th>Available</th><th>Last login</th><th>Status</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((u) => (
                <tr key={u.id} style={{ opacity: u.is_active ? 1 : 0.5 }}>
                  <td>
                    <div><strong>{u.first_name || u.username}</strong></div>
                    <div className="small muted">{u.username}{u.email ? ` \u00b7 ${u.email}` : ""}</div>
                  </td>
                  <td>
                    <select className="inline-select" value={u.role} onChange={(e) => update(u.id, { role: e.target.value })}>
                      {ROLES.map((r) => <option key={r} value={r}>{roleLabels[r]}</option>)}
                    </select>
                  </td>
                  <td>
                    <select
                      className="inline-select"
                      value={u.society || ""}
                      onChange={(e) => update(u.id, { society: e.target.value ? Number(e.target.value) : null })}
                    >
                      <option value="">None</option>
                      {societies.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                    </select>
                  </td>
                  <td className="small">{u.phone || "-"}</td>
                  <td className="small">
                    {["VOLUNTEER", "SECURITY"].includes(u.role) ? (u.is_available ? "Yes" : "No") : "-"}
                  </td>
                  <td className="small muted">{when(u.last_login)}</td>
                  <td>
                    <button
                      className={`btn btn-sm ${u.is_active ? "btn-ghost" : ""}`}
                      disabled={u.id === me?.id}
                      onClick={() => update(u.id, { is_active: !u.is_active })}
                    >
                      {u.is_active ? "Deactivate" : "Activate"}
                    </button>
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