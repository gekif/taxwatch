const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const isBrowser = () => typeof window !== "undefined";
export const getToken = () => (isBrowser() ? sessionStorage.getItem("token") : null);

export function getUser() {
  if (!isBrowser()) return null;
  try {
    return JSON.parse(sessionStorage.getItem("user") || "null");
  } catch {
    return null;
  }
}

export function saveSession(data) {
  sessionStorage.setItem("token", data.access_token);
  sessionStorage.setItem(
    "user",
    JSON.stringify({ username: data.username, role: data.role, full_name: data.full_name })
  );
}

export function clearSession() {
  sessionStorage.clear();
}

/** Thin fetch wrapper: bearer auth, JSON/form bodies, readable errors, auto-logout on 401. */
export async function api(path, { method = "GET", body, form } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  let payload;
  if (form) {
    payload = new URLSearchParams(form);
  } else if (body) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }
  const res = await fetch(`${BASE}${path}`, { method, headers, body: payload });
  if (res.status === 401 && token) {
    clearSession();
    window.location.href = "/";
    throw new Error("Session expired");
  }
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const d = data?.detail;
    throw new Error(
      typeof d === "string" ? d : Array.isArray(d) ? d.map((x) => x.msg).join("; ") : "Request failed"
    );
  }
  return data;
}

export const rupiah = (n) =>
  new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(n ?? 0);
