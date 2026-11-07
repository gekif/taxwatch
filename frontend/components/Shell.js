"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { clearSession, getToken, getUser } from "../lib/api";

const LINKS = [
  { href: "/dashboard", label: "Dashboard", roles: ["admin", "officer", "auditor"] },
  { href: "/taxpayers", label: "Taxpayers", roles: ["admin", "officer", "auditor"] },
  { href: "/transactions", label: "Transactions", roles: ["admin", "officer", "auditor"] },
  { href: "/audit", label: "Audit trail", roles: ["admin", "auditor"] },
];

export default function Shell({ children }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState(null);

  useEffect(() => {
    if (!getToken()) router.replace("/");
    else setUser(getUser());
  }, [router]);

  if (!user) return null;
  const logout = () => {
    clearSession();
    router.replace("/");
  };
  return (
    <>
      <nav className="nav">
        <strong>TaxWatch</strong>
        {LINKS.filter((l) => l.roles.includes(user.role)).map((l) => (
          <Link key={l.href} href={l.href} className={pathname === l.href ? "active" : ""}>
            {l.label}
          </Link>
        ))}
        <span className="spacer" />
        <span className="muted">
          {user.full_name} ({user.role})
        </span>
        <button onClick={logout}>Log out</button>
      </nav>
      <main className="container">{children}</main>
    </>
  );
}
