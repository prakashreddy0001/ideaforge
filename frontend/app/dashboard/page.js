"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import AnimatedBackground from "@/components/AnimatedBackground";

export default function DashboardPage() {
  const { user, profile, loading } = useAuth();
  const router = useRouter();

  if (loading) {
    return (
      <main className="dashboard-page">
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

  if (!user) {
    router.push("/login");
    return null;
  }

  const usage = profile?.usage;
  const usedPercent =
    usage && usage.limit > 0 ? Math.min(100, (usage.used / usage.limit) * 100) : 0;

  return (
    <>
      <AnimatedBackground />
      <main className="dashboard-page">
        <h1 className="dashboard-title">Dashboard</h1>

        <div className="dashboard-grid">
          {/* Profile Card */}
          <div className="glass-card dashboard-card">
            <h2 className="card-title">Profile</h2>
            <div className="dashboard-profile-info">
              <p className="dashboard-email">{profile?.email}</p>
              <span className={`tier-badge tier-badge--${profile?.tier}`}>
                {profile?.tier}
              </span>
            </div>
            {profile?.role === "admin" && (
              <span className="role-badge">Admin</span>
            )}
          </div>

          {/* Usage Card */}
          <div className="glass-card dashboard-card">
            <h2 className="card-title">Usage This Month</h2>
            {usage && (
              <>
                <div className="usage-stats">
                  <span className="usage-big-number">{usage.used}</span>
                  <span className="usage-divider">/</span>
                  <span className="usage-limit">
                    {usage.limit === -1 ? "Unlimited" : usage.limit}
                  </span>
                </div>
                {usage.limit !== -1 && (
                  <div className="usage-meter">
                    <div
                      className="usage-meter-fill"
                      style={{ width: `${usedPercent}%` }}
                    />
                  </div>
                )}
                {usage.limit !== -1 && (
                  <p className="usage-remaining">
                    {usage.remaining} generations remaining
                  </p>
                )}
              </>
            )}
          </div>

          {/* Plan Card */}
          <div className="glass-card dashboard-card">
            <h2 className="card-title">Your Plan</h2>
            <div className="dashboard-manage">
              <p className="dashboard-plan-label">
                Current plan: <strong>{profile?.tier}</strong>
              </p>
              {profile?.tier === "free" && (
                <Link href="/pricing" className="neon-btn">
                  View Plans
                </Link>
              )}
            </div>
          </div>
        </div>

        <div className="dashboard-actions">
          <Link href="/generate" className="neon-btn">
            Generate New Idea
          </Link>
        </div>
      </main>
    </>
  );
}
