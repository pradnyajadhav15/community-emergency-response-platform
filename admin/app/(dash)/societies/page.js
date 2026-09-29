"use client";

import { useEffect, useState } from "react";

import api, { apiError } from "@/lib/api";
import { fetchAll } from "@/lib/fetchAll";

function AddForm({ fields, onSubmit, label }) {
  const empty = Object.fromEntries(fields.map((f) => [f.key, ""]));
  const [form, setForm] = useState(empty);
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    const ok = await onSubmit(form);
    setBusy(false);
    if (ok) setForm(empty);
  }

  return (
    <form onSubmit={submit} className="mt">
      {fields.map((f) => (
        <div className="field" key={f.key}>
          <label>{f.label}</label>
          <input
            type={f.type || "text"}
            value={form[f.key]}
            onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
            placeholder={f.placeholder}
          />
        </div>
      ))}
      <button className="btn btn-sm" disabled={busy}>{busy ? "Saving..." : label}</button>
    </form>
  );
}

export default function Societies() {
  const [societies, setSocieties] = useState([]);
  const [blocks, setBlocks] = useState([]);
  const [flats, setFlats] = useState([]);
  const [society, setSociety] = useState(null);
  const [block, setBlock] = useState(null);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");

  async function loadSocieties() {
    try {
      setSocieties(await fetchAll("/societies/"));
    } catch (e) {
      setError(apiError(e, "Could not load societies."));
    }
  }

  async function pickSociety(s) {
    setSociety(s);
    setBlock(null);
    setFlats([]);
    setBlocks(await fetchAll(`/blocks/?society=${s.id}`));
  }

  async function pickBlock(b) {
    setBlock(b);
    setFlats(await fetchAll(`/flats/?block=${b.id}`));
  }

  useEffect(() => { loadSocieties(); }, []);

  async function create(path, payload, after, message) {
    setError("");
    setOk("");
    try {
      await api.post(path, payload);
      await after();
      setOk(message);
      return true;
    } catch (e) {
      setError(apiError(e, "Could not save."));
      return false;
    }
  }

  return (
    <>
      <h1 className="page-title">Societies</h1>
      <p className="page-sub">Manage societies, blocks, and flats. Select a society to drill down.</p>

      {error && <div className="banner banner-error">{error}</div>}
      {ok && <div className="banner banner-ok">{ok}</div>}

      <div className="grid grid-3">
        <div className="card">
          <div className="card-title">Societies ({societies.length})</div>
          {societies.length === 0 && <div className="empty">None yet.</div>}
          {societies.map((s) => (
            <div
              key={s.id}
              className={`list-item ${society?.id === s.id ? "active" : ""}`}
              onClick={() => pickSociety(s)}
            >
              <div><strong>{s.name}</strong></div>
              <div className="small muted">{s.code} &middot; {s.city || "no city"} &middot; {s.block_count} blocks</div>
            </div>
          ))}
          <AddForm
            label="Add Society"
            fields={[
              { key: "name", label: "Name", placeholder: "Green Valley Residency" },
              { key: "code", label: "Join code", placeholder: "GVR002" },
              { key: "city", label: "City", placeholder: "Pune" },
            ]}
            onSubmit={(f) => create("/societies/", f, loadSocieties, `Society "${f.name}" created.`)}
          />
        </div>

        <div className="card">
          <div className="card-title">Blocks {society ? `in ${society.name}` : ""}</div>
          {!society && <div className="empty">Select a society.</div>}
          {society && blocks.length === 0 && <div className="empty">No blocks yet.</div>}
          {blocks.map((b) => (
            <div
              key={b.id}
              className={`list-item ${block?.id === b.id ? "active" : ""}`}
              onClick={() => pickBlock(b)}
            >
              <div><strong>{b.name}</strong></div>
              <div className="small muted">{b.total_floors} floors &middot; {b.flat_count} flats</div>
            </div>
          ))}
          {society && (
            <AddForm
              label="Add Block"
              fields={[
                { key: "name", label: "Block name", placeholder: "B Wing" },
                { key: "total_floors", label: "Floors", type: "number", placeholder: "5" },
              ]}
              onSubmit={(f) =>
                create(
                  "/blocks/",
                  { society: society.id, name: f.name, total_floors: Number(f.total_floors) || 1 },
                  () => pickSociety(society),
                  `Block "${f.name}" added.`
                )
              }
            />
          )}
        </div>

        <div className="card">
          <div className="card-title">Flats {block ? `in ${block.name}` : ""}</div>
          {!block && <div className="empty">Select a block.</div>}
          {block && flats.length === 0 && <div className="empty">No flats yet.</div>}
          {flats.map((f) => (
            <div key={f.id} className="list-item">
              <strong>{f.flat_number}</strong> <span className="small muted">&middot; floor {f.floor}</span>
            </div>
          ))}
          {block && (
            <AddForm
              label="Add Flat"
              fields={[
                { key: "flat_number", label: "Flat number", placeholder: "B-201" },
                { key: "floor", label: "Floor", type: "number", placeholder: "2" },
              ]}
              onSubmit={(f) =>
                create(
                  "/flats/",
                  { block: block.id, flat_number: f.flat_number, floor: Number(f.floor) || 0 },
                  () => pickBlock(block),
                  `Flat ${f.flat_number} added.`
                )
              }
            />
          )}
        </div>
      </div>
    </>
  );
}