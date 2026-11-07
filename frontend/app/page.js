"use client";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api, saveSession } from "../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      saveSession(await api("/api/auth/login", { method: "POST", form: { username, password } }));
      router.push("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card login">
      <h2>TaxWatch</h2>
      <p className="muted">Regional tax transaction monitoring</p>
      <form onSubmit={submit}>
        <input aria-label="Username" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
        <input aria-label="Password" type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        {error && <div className="error" role="alert">{error}</div>}
        <button disabled={busy}>{busy ? "Signing in..." : "Sign in"}</button>
      </form>
    </div>
  );
}
