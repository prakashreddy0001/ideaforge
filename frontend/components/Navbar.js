"use client";

import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";

export default function Navbar() {
  const { user, profile, loading, signOut } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link href="/" className="navbar-brand">
          IdeaForge
        </Link>

        <div className="navbar-links">
          <Link href="/" className="navbar-link">
            Home
          </Link>
          <Link href="/generate" className="navbar-link">
            Generate
          </Link>
          <Link href="/refine" className="navbar-link">
            Refine
          </Link>
          <Link href="/pricing" className="navbar-link">
            Pricing
          </Link>
        </div>

        <div className="navbar-actions">
          {loading ? (
            <span className="navbar-skeleton" />
          ) : user ? (
            <>
              {profile?.role === "admin" && (
                <Link href="/admin" className="navbar-link navbar-link--admin">
                  Admin
                </Link>
              )}
              <Link href="/dashboard" className="navbar-link">
                Dashboard
              </Link>
              <button onClick={signOut} className="navbar-btn navbar-btn--ghost">
                Sign Out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="navbar-btn navbar-btn--ghost">
                Log In
              </Link>
              <Link href="/register" className="navbar-btn navbar-btn--primary">
                Sign Up
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
