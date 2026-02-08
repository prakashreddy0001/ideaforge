"use client";

import { useState, useEffect } from "react";
import { authFetch } from "@/lib/auth-fetch";
import { API_URL } from "@/lib/constants";

export default function AdminOverview() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchStats() {
      try {
        const res = await authFetch(`${API_URL}/api/admin/analytics/overview`);
        if (res.ok) {
          setStats(await res.json());
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchStats();
  }, []);

  if (loading) {
    return <div className="admin-loading">Loading overview...</div>;
  }

  const cards = [
    { label: "Total Users", value: stats?.total_users ?? 0, color: "purple" },
    { label: "Active Users", value: stats?.active_users ?? 0, color: "green" },
    { label: "Pro Users", value: stats?.pro_users ?? 0, color: "blue" },
    { label: "Enterprise Users", value: stats?.enterprise_users ?? 0, color: "gold" },
    {
      label: "Total Generations",
      value: stats?.total_generations ?? 0,
      color: "cyan",
    },
  ];

  return (
    <div>
      <h1 className="admin-page-title">Overview</h1>
      <div className="stat-grid">
        {cards.map((c) => (
          <div key={c.label} className={`stat-card stat-card--${c.color} glass-card`}>
            <span className="stat-label">{c.label}</span>
            <span className="stat-value">{c.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
