"use client";
import { useCallback, useEffect, useState } from "react";
import Shell from "../../components/Shell";
import { api, getUser } from "../../lib/api";

const EMPTY = { npwpd: "", name: "", address: "", category: "hotel" };

export default function TaxpayersPage() {
  const [page, setPage] = useState({ total: 0, items: [] });
  const [q, setQ] = useState("");
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState("");
  const role = getUser()?.role;
  const canWrite = role === "admin" || role === "officer";

  const load = useCallback(() => {
    api(`/api/taxpayers?limit=50&q=${encodeURIComponent(q)}`).then(setPage).catch((e) => setError(e.message));
  }, [q]);
  useEffect(load, [load]);

  async function create(e) {
    e.preventDefault();
    setError("");
    try {
      await api("/api/taxpayers", { method: "POST", body: form });
      setForm(EMPTY);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function remove(id) {
    if (!confirm("Deactivate this taxpayer?")) return;
    try {
      await api(`/api/taxpayers/${id}`, { method: "DELETE" });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <Shell>
      <h2>Taxpayers ({page.total})</h2>
      {error && <div className="error" role="alert">{error}</div>}
      {canWrite && (
        <form className="card row" onSubmit={create}>
          <input placeholder="NPWPD (e.g. HTL000009)" value={form.npwpd} onChange={(e) => setForm({ ...form, npwpd: e.target.value.toUpperCase() })} required />
          <input placeholder="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          <input placeholder="Address" value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
          <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}>
            {["hotel", "restoran", "hiburan", "parkir"].map((c) => <option key={c}>{c}</option>)}
          </select>
          <button>Add taxpayer</button>
        </form>
      )}
      <div className="row"><input placeholder="Search name or NPWPD" value={q} onChange={(e) => setQ(e.target.value)} /></div>
      <div className="card table-wrap">
        <table>
          <thead><tr><th>NPWPD</th><th>Name</th><th>Category</th><th /></tr></thead>
          <tbody>
            {page.items.map((t) => (
              <tr key={t.id}>
                <td>{t.npwpd}</td><td>{t.name}</td><td>{t.category}</td>
                <td>{role === "admin" && <button className="secondary" onClick={() => remove(t.id)}>Deactivate</button>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Shell>
  );
}
