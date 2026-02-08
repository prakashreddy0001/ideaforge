"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { authFetch } from "@/lib/auth-fetch";
import { API_URL } from "@/lib/constants";

export default function AdminUserDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const [userData, setUserData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  // Editable fields
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("user");
  const [tier, setTier] = useState("free");
  const [isActive, setIsActive] = useState(true);

  useEffect(() => {
    async function fetchUser() {
      try {
        const res = await authFetch(`${API_URL}/api/admin/users/${id}`);
        if (res.ok) {
          const data = await res.json();
          setUserData(data);
          setFullName(data.profile.full_name || "");
          setRole(data.profile.role);
          setTier(data.profile.tier);
          setIsActive(data.profile.is_active);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    fetchUser();
  }, [id]);

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      const res = await authFetch(`${API_URL}/api/admin/users/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: fullName,
          role,
          tier,
          is_active: isActive,
        }),
      });

      if (res.ok) {
        setMessage("User updated successfully.");
      } else {
        const data = await res.json();
        setMessage(data.detail || "Failed to update.");
      }
    } catch (err) {
      setMessage("Error saving changes.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="admin-loading">Loading user...</div>;
  }

  if (!userData) {
    return <div className="admin-loading">User not found.</div>;
  }

  const profile = userData.profile;

  return (
    <div>
      <button
        className="admin-back-btn"
        onClick={() => router.push("/admin/users")}
      >
        &larr; Back to Users
      </button>

      <h1 className="admin-page-title">{profile.email}</h1>

      <div className="admin-detail-grid">
        {/* Edit Form */}
        <div className="glass-card admin-detail-card">
          <h2 className="card-title">Edit User</h2>

          <label className="form-label">Full Name</label>
          <input
            type="text"
            className="input auth-input"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />

          <label className="form-label">Role</label>
          <select
            className="input auth-input"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>

          <label className="form-label">Tier</label>
          <select
            className="input auth-input"
            value={tier}
            onChange={(e) => setTier(e.target.value)}
          >
            <option value="free">Free</option>
            <option value="pro">Pro</option>
            <option value="enterprise">Enterprise</option>
          </select>

          <label className="admin-toggle-label">
            <input
              type="checkbox"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
            />
            <span>Account Active</span>
          </label>

          {message && <p className="admin-message">{message}</p>}

          <button
            className="neon-btn"
            onClick={handleSave}
            disabled={saving}
            style={{ marginTop: 16 }}
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>

        {/* Info Card */}
        <div className="glass-card admin-detail-card">
          <h2 className="card-title">Info</h2>
          <dl className="admin-dl">
            <dt>User ID</dt>
            <dd className="admin-mono">{profile.id}</dd>
            <dt>Created</dt>
            <dd>{new Date(profile.created_at).toLocaleString()}</dd>
            <dt>Total Generations</dt>
            <dd>{userData.total_generations}</dd>
            {userData.subscription && (
              <>
                <dt>Subscription Status</dt>
                <dd>{userData.subscription.status}</dd>
                <dt>Stripe Sub ID</dt>
                <dd className="admin-mono">
                  {userData.subscription.stripe_subscription_id || "—"}
                </dd>
              </>
            )}
          </dl>
        </div>
      </div>

      {/* Recent Usage */}
      {userData.recent_usage.length > 0 && (
        <div className="glass-card" style={{ marginTop: 20 }}>
          <h2 className="card-title">Recent Generations</h2>
          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Mode</th>
                  <th>Tool</th>
                  <th>Idea Summary</th>
                </tr>
              </thead>
              <tbody>
                {userData.recent_usage.map((u, i) => (
                  <tr key={i}>
                    <td>{new Date(u.created_at).toLocaleString()}</td>
                    <td>{u.mode || "—"}</td>
                    <td>{u.tool || "default"}</td>
                    <td className="admin-idea-cell">
                      {u.idea_summary || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
