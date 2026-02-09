"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { useState } from "react";

/* ── Inline SVG icons (Feather-style, 18×18) ── */

const Icon = ({ d, ...props }) => (
  <svg
    width="18"
    height="18"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    {...props}
  >
    {typeof d === "string" ? <path d={d} /> : d}
  </svg>
);

const icons = {
  home: (
    <Icon
      d={
        <>
          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
          <polyline points="9 22 9 12 15 12 15 22" />
        </>
      }
    />
  ),
  generate: (
    <Icon d={<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />} />
  ),
  refine: (
    <Icon
      d={
        <>
          <path d="M12 2L15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2z" />
        </>
      }
    />
  ),
  pricing: (
    <Icon
      d={
        <>
          <line x1="12" y1="1" x2="12" y2="23" />
          <path d="M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6" />
        </>
      }
    />
  ),
  dashboard: (
    <Icon
      d={
        <>
          <rect x="3" y="3" width="7" height="7" />
          <rect x="14" y="3" width="7" height="7" />
          <rect x="14" y="14" width="7" height="7" />
          <rect x="3" y="14" width="7" height="7" />
        </>
      }
    />
  ),
  admin: (
    <Icon
      d={
        <>
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </>
      }
    />
  ),
  users: (
    <Icon
      d={
        <>
          <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
          <circle cx="9" cy="7" r="4" />
          <path d="M23 21v-2a4 4 0 00-3-3.87" />
          <path d="M16 3.13a4 4 0 010 7.75" />
        </>
      }
    />
  ),
  analytics: (
    <Icon
      d={
        <>
          <line x1="18" y1="20" x2="18" y2="10" />
          <line x1="12" y1="20" x2="12" y2="4" />
          <line x1="6" y1="20" x2="6" y2="14" />
        </>
      }
    />
  ),
  logout: (
    <Icon
      d={
        <>
          <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
          <polyline points="16 17 21 12 16 7" />
          <line x1="21" y1="12" x2="9" y2="12" />
        </>
      }
    />
  ),
};

const NAV_MAIN = [
  { href: "/", label: "Home", icon: icons.home },
  { href: "/generate", label: "Generate", icon: icons.generate },
  { href: "/refine", label: "Refine", icon: icons.refine },
  { href: "/pricing", label: "Pricing", icon: icons.pricing },
];

const NAV_ACCOUNT = [
  { href: "/dashboard", label: "Dashboard", icon: icons.dashboard },
];

const NAV_ADMIN = [
  { href: "/admin", label: "Overview", icon: icons.admin, exact: true },
  { href: "/admin/users", label: "Users", icon: icons.users },
  { href: "/admin/analytics", label: "Analytics", icon: icons.analytics },
];

export default function Navbar() {
  const { user, profile, loading, signOut } = useAuth();
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (href, exact) => {
    if (exact || href === "/") return pathname === href;
    return pathname.startsWith(href);
  };

  const close = () => setMobileOpen(false);

  const renderLinks = (items) =>
    items.map((item) => (
      <Link
        key={item.href}
        href={item.href}
        className={`sidebar-link ${isActive(item.href, item.exact) ? "sidebar-link--active" : ""}`}
        onClick={close}
      >
        <span className="sidebar-link-icon">{item.icon}</span>
        <span className="sidebar-link-label">{item.label}</span>
      </Link>
    ));

  return (
    <>
      {/* Mobile toggle */}
      <button
        className="sidebar-toggle"
        onClick={() => setMobileOpen((o) => !o)}
        aria-label="Toggle menu"
      >
        <span className={`sidebar-hamburger ${mobileOpen ? "sidebar-hamburger--open" : ""}`}>
          <span />
          <span />
          <span />
        </span>
      </button>

      {/* Overlay */}
      {mobileOpen && (
        <div className="sidebar-overlay" onClick={close} />
      )}

      {/* Sidebar */}
      <aside className={`sidebar ${mobileOpen ? "sidebar--open" : ""}`}>
        {/* Brand */}
        <div className="sidebar-header">
          <Link href="/" className="sidebar-brand" onClick={close}>
            <span className="sidebar-brand-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path
                  d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"
                  fill="url(#brand-grad)"
                />
                <defs>
                  <linearGradient id="brand-grad" x1="3" y1="2" x2="21" y2="22">
                    <stop stopColor="#a855f7" />
                    <stop offset="1" stopColor="#3b82f6" />
                  </linearGradient>
                </defs>
              </svg>
            </span>
            <span className="sidebar-brand-text">IdeaForge</span>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          <div className="sidebar-section">
            <span className="sidebar-section-label">Menu</span>
            {renderLinks(NAV_MAIN)}
          </div>

          {user && (
            <div className="sidebar-section">
              <span className="sidebar-section-label">Account</span>
              {renderLinks(NAV_ACCOUNT)}
            </div>
          )}

          {profile?.role === "admin" && (
            <div className="sidebar-section">
              <span className="sidebar-section-label">Admin</span>
              {renderLinks(NAV_ADMIN)}
            </div>
          )}
        </nav>

        {/* Footer */}
        <div className="sidebar-footer">
          {loading ? (
            <div className="sidebar-skeleton" />
          ) : user ? (
            <div className="sidebar-user">
              <div className="sidebar-user-info">
                <span className="sidebar-user-email">
                  {profile?.full_name || profile?.email || user.email}
                </span>
                <span className={`tier-badge tier-badge--${profile?.tier || "free"}`}>
                  {profile?.tier || "free"}
                </span>
              </div>
              <button onClick={signOut} className="sidebar-signout">
                {icons.logout}
                <span>Sign Out</span>
              </button>
            </div>
          ) : (
            <div className="sidebar-auth">
              <Link href="/login" className="sidebar-auth-btn sidebar-auth-btn--ghost" onClick={close}>
                Log In
              </Link>
              <Link href="/register" className="sidebar-auth-btn sidebar-auth-btn--primary" onClick={close}>
                Sign Up
              </Link>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
