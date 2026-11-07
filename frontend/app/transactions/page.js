"use client";
import { useCallback, useEffect, useState } from "react";
import Shell from "../../components/Shell";
import { api, getUser, rupiah } from "../../lib/api";

const LIMIT = 15;
// Local calendar date (toISOString would give the UTC date, which can be off by one day).
const today = () => {
  const d = new Date();
  return new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
};

export default function TransactionsPage() {
  const [page, setPage] = useState({ total: 0, items: [] });
  const [taxpayers, setTaxpayers] = useState([]);
  const [skip, setSkip] = useState(0);
  const [flaggedOnly, setFlaggedOnly] = useState(false);
  const [form, setForm] = useState({ taxpayer_id: "", amount: "", trx_date: today() });
  const [error, setError] = useState("");
  const role = getUser()?.role;

  const load = useCallback(() => {
    api(`/api/transactions?limit=${LIMIT}&skip=${skip}&flagged_only=${flaggedOnly}`)
      .then(setPage)
      .catch((e) => setError(e.message));
  }, [skip, flaggedOnly]);
  useEffect(load, [load]);
  useEffect(() => {
    api("/api/taxpayers?limit=100").then((p) => setTaxpayers(p.items)).catch(() => {});
  }, []);

  async function create(e) {
    e.preventDefault();
    setError("");
    try {
      await api("/api/transactions", {
        method: "POST",
        body: { taxpayer_id: Number(form.taxpayer_id), amount: Number(form.amount), trx_date: form.trx_date },
      });
      setForm({ ...form, amount: "" });
      setSkip(0);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function clearFlag(id) {
    try {
      await api(`/api/transactions/${id}/clear-flag`, { method: "POST" });
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <Shell>
      <h2>Transactions ({page.total})</h2>
      {error && <div className="error" role="alert">{error}</div>}
      {(role === "admin" || role === "officer") && (
        <form className="card row" onSubmit={create}>
          <select value={form.taxpayer_id} onChange={(e) => setForm({ ...form, taxpayer_id: e.target.value })} required>
            <option value="">Select taxpayer</option>
            {taxpayers.map((t) => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
          <input type="number" min="1" placeholder="Amount (IDR)" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} required />
          <input type="date" max={today()} value={form.trx_date} onChange={(e) => setForm({ ...form, trx_date: e.target.value })} required />
          <button>Record transaction</button>
        </form>
      )}
      <label className="row">
        <input type="checkbox" checked={flaggedOnly} onChange={(e) => { setSkip(0); setFlaggedOnly(e.target.checked); }} />
        Show flagged only
      </label>
      <div className="card table-wrap">
        <table>
          <thead><tr><th>Date</th><th>Taxpayer</th><th>Amount</th><th>Tax</th><th>Status</th><th /></tr></thead>
          <tbody>
            {page.items.map((t) => (
              <tr key={t.id}>
                <td>{t.trx_date}</td><td>{t.taxpayer_name}</td><td>{rupiah(t.amount)}</td><td>{rupiah(t.tax_amount)}</td>
                <td>{t.is_flagged && <span className="badge">{t.flag_reason}</span>}</td>
                <td>{t.is_flagged && (role === "admin" || role === "auditor") && <button className="secondary" onClick={() => clearFlag(t.id)}>Clear flag</button>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="row">
        <button className="secondary" disabled={skip === 0} onClick={() => setSkip(Math.max(0, skip - LIMIT))}>Previous</button>
        <span className="muted">{page.total === 0 ? 0 : skip + 1}-{Math.min(skip + LIMIT, page.total)} of {page.total}</span>
        <button className="secondary" disabled={skip + LIMIT >= page.total} onClick={() => setSkip(skip + LIMIT)}>Next</button>
      </div>
    </Shell>
  );
}
