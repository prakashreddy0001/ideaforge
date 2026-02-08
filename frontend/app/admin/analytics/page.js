"use client";

import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from "recharts";
import { createClient } from "@/lib/supabase/client";
import { API_URL } from "@/lib/constants";

const COLORS = {
  free: "#a855f7",
  pro: "#3b82f6",
  enterprise: "#f59e0b",
};

export default function AdminAnalyticsPage() {
  const [tierData, setTierData] = useState([]);
  const [dailyData, setDailyData] = useState([]);
  const [modeData, setModeData] = useState([]);
  const [toolData, setToolData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const supabase = createClient();
        const {
          data: { session },
        } = await supabase.auth.getSession();
        const headers = { Authorization: `Bearer ${session.access_token}` };

        const [tiersRes, usageRes] = await Promise.all([
          fetch(`${API_URL}/api/admin/analytics/tiers`, { headers }),
          fetch(`${API_URL}/api/admin/analytics/usage?days=30`, { headers }),
        ]);

        if (tiersRes.ok) {
          const data = await tiersRes.json();
          setTierData(data.tiers);
        }

        if (usageRes.ok) {
          const data = await usageRes.json();
          processDailyData(data.usage);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchAnalytics();
  }, []);

  function processDailyData(usage) {
    const byDay = {};
    const modes = {};
    const tools = {};

    usage.forEach((u) => {
      const day = u.created_at.split("T")[0];
      byDay[day] = (byDay[day] || 0) + 1;

      const mode = u.mode || "unknown";
      modes[mode] = (modes[mode] || 0) + 1;

      const tool = u.tool || "default";
      tools[tool] = (tools[tool] || 0) + 1;
    });

    setDailyData(
      Object.entries(byDay)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([date, count]) => ({
          date: date.slice(5),
          count,
        }))
    );

    setModeData(
      Object.entries(modes).map(([name, value]) => ({ name, value }))
    );

    setToolData(
      Object.entries(tools).map(([name, value]) => ({ name, value }))
    );
  }

  if (loading) {
    return <div className="admin-loading">Loading analytics...</div>;
  }

  return (
    <div>
      <h1 className="admin-page-title">Analytics</h1>

      <div className="analytics-grid">
        {/* Daily Generations */}
        <div className="glass-card analytics-chart-card">
          <h2 className="card-title">Daily Generations (30 days)</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={dailyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="date" stroke="#8b8aa0" fontSize={11} />
                <YAxis stroke="#8b8aa0" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    background: "#12121a",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: 8,
                    color: "#e8e6f0",
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="count"
                  stroke="#a855f7"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Tier Distribution */}
        <div className="glass-card analytics-chart-card">
          <h2 className="card-title">User Tiers</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={tierData}
                  dataKey="count"
                  nameKey="tier"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ tier, count }) => `${tier}: ${count}`}
                >
                  {tierData.map((entry) => (
                    <Cell
                      key={entry.tier}
                      fill={COLORS[entry.tier] || "#a855f7"}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "#12121a",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: 8,
                    color: "#e8e6f0",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Generations by Mode */}
        <div className="glass-card analytics-chart-card">
          <h2 className="card-title">By Mode</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={modeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="name" stroke="#8b8aa0" fontSize={11} />
                <YAxis stroke="#8b8aa0" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    background: "#12121a",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: 8,
                    color: "#e8e6f0",
                  }}
                />
                <Bar dataKey="value" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Generations by Tool */}
        <div className="glass-card analytics-chart-card">
          <h2 className="card-title">By Tool</h2>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={toolData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis dataKey="name" stroke="#8b8aa0" fontSize={11} />
                <YAxis stroke="#8b8aa0" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    background: "#12121a",
                    border: "1px solid rgba(255,255,255,0.08)",
                    borderRadius: 8,
                    color: "#e8e6f0",
                  }}
                />
                <Bar dataKey="value" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
