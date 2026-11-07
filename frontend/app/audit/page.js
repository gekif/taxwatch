"use client";
import { useEffect, useState } from "react";
import Shell from "../../components/Shell";
import { api } from "../../lib/api";

export default function AuditPage() {
  const [page, setPage] = useState({ total: 0, items: [] });
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/audit?limit=50").then(setPage).catch((e) => setError(e.message));
  }, []);

  return (
    <Shell>
      <h2>Audit trail ({page.total})</h2>
      {error && <div className="error">{error}</div>}
      <div className="card table-wrap">
        <table>
          <thead><tr><th>Time</th><th>Actor</th><th>Action</th><th>Entity</th><th>Detail</th></tr></thead>
          <tbody>
            {page.items.map((a) => (
              <tr key={a.id}>
                <td>{new Date(a.created_at).toLocaleString()}</td><td>{a.actor}</td><td>{a.action}</td>
                <td>{a.entity} #{a.entity_id}</td><td>{a.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Shell>
  );
}
