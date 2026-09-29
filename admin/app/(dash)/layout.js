"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/lib/auth";
import { roleLabels } from "@/lib/format";

const NAV = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/alerts", label: "Alerts" },
  { href: "/societies", label: "Societies" },
  { href: "/users", label: "Users" },
];

export default function DashLayout({ children }) {
  const { user, loading, signOut } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [user, loading, router]);

  if (loading || !user) return <div className="empty">Loading...</div>;

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">CERP</div>
        <div className="brand-sub">ADMIN PORTAL</div>

        <nav className="nav">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={`nav-item ${pathname.startsWith(item.href) ? "active" : ""}`}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="sidebar-foot">
          <div className="sidebar-user">{user.first_name || user.username}</div>
          <div className="sidebar-role">{roleLabels[user.role] || user.role}</div>
          <button className="btn btn-ghost btn-sm" onClick={signOut} style={{ width: "100%" }}>
            Sign Out
          </button>
        </div>
      </aside>

      <main className="main">{children}</main>
    </div>
  );
}