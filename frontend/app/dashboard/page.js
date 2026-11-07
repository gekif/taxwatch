"use client";
import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import Shell from "../../components/Shell";
import { api, rupiah } from "../../lib/api";

export default function DashboardPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/dashboard/summary").then(setData).catch((e) => setError(e.message));
  }, []);

  return (
    <Shell>
      <h2>Dashboard</h2>
      {error && <div className="error">{error}</div>}
      {data && (
        <>
          <div className="grid">
            <div className="card"><div className="muted">Taxpayers</div><div className="stat">{data.taxpayers}</div></div>
            <div className="card"><div className="muted">Transactions</div><div className="stat">{data.transactions}</div></div>
            <div className="card"><div className="muted">Total tax</div><div className="stat">{rupiah(data.total_tax)}</div></div>
            <div className="card"><div className="muted">Flagged for review</div><div className="stat">{data.flagged}</div></div>
          </div>
          <div className="card">
            <h3>Monthly tax revenue</h3>
            <div style={{ height: 280 }}>
              <ResponsiveContainer>
                <BarChart data={data.monthly}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis tickFormatter={(v) => `${Math.round(v / 1e6)}M`} />
                  <Tooltip formatter={(v) => rupiah(v)} />
                  <Bar dataKey="tax" fill="#1d4ed8" name="Tax" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="card table-wrap">
            <h3>By category</h3>
            <table>
              <thead><tr><th>Category</th><th>Transactions</th><th>Amount</th><th>Tax</th></tr></thead>
              <tbody>
                {data.by_category.map((c) => (
                  <tr key={c.category}><td>{c.category}</td><td>{c.transactions}</td><td>{rupiah(c.amount)}</td><td>{rupiah(c.tax)}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </Shell>
  );
}
