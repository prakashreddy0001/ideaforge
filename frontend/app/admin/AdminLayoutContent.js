"use client";

import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";
import AnimatedBackground from "@/components/AnimatedBackground";

const NAV_ITEMS = [
  { href: "/admin", label: "Overview" },
  { href: "/admin/users", label: "Users" },
  { href: "/admin/analytics", label: "Analytics" },
];

export default function AdminLayoutContent({ children }) {
  const { profile, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && (!profile || profile.role !== "admin")) {
      router.push("/dashboard");
    }
  }, [loading, profile, router]);

  if (loading) {
    return (
      <main className="admin-page">
        <div className="loading-container">
          <div className="typing-dots">
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
          </div>
        </div>
      </main>
    );
  }

  if (!profile || profile.role !== "admin") {
    return null;
  }

  return (
    <>
      <AnimatedBackground />
      <div className="admin-layout">
        <aside className="admin-sidebar glass-card">
          <h2 className="admin-sidebar-title">Admin Panel</h2>
          <nav className="admin-nav">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`admin-nav-link ${
                  pathname === item.href ? "admin-nav-link--active" : ""
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </aside>
        <main className="admin-content">{children}</main>
      </div>
    </>
  );
}
