"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { authFetch } from "@/lib/auth-fetch";
import { API_URL } from "@/lib/constants";

export default function AdminUsersPage() {
  const [users, setUsers] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [tierFilter, setTierFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const perPage = 20;

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page, per_page: perPage });
      if (search) params.set("search", search);
      if (roleFilter) params.set("role", roleFilter);
      if (tierFilter) params.set("tier", tierFilter);

      const res = await authFetch(`${API_URL}/api/admin/users?${params}`);
      if (res.ok) {
        const data = await res.json();
        setUsers(data.users);
        setTotal(data.total);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [page, search, roleFilter, tierFilter]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const totalPages = Math.ceil(total / perPage);

  return (
    <div>
      <h1 className="admin-page-title">Users ({total})</h1>

      <div className="admin-filters">
        <input
          type="text"
          className="input admin-search"
          placeholder="Search by email or name..."
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <select
          className="input admin-select"
          value={roleFilter}
          onChange={(e) => {
            setRoleFilter(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All Roles</option>
          <option value="user">User</option>
          <option value="admin">Admin</option>
        </select>
        <select
          className="input admin-select"
          value={tierFilter}
          onChange={(e) => {
            setTierFilter(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All Tiers</option>
          <option value="free">Free</option>
          <option value="pro">Pro</option>
          <option value="enterprise">Enterprise</option>
        </select>
      </div>

      {loading ? (
        <div className="admin-loading">Loading users...</div>
      ) : (
        <>
          <div className="data-table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Tier</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.email}</td>
                    <td>{u.full_name || "—"}</td>
                    <td>
                      <span className={`role-badge role-badge--${u.role}`}>
                        {u.role}
                      </span>
                    </td>
                    <td>
                      <span className={`tier-badge tier-badge--${u.tier}`}>
                        {u.tier}
                      </span>
                    </td>
                    <td>
                      <span
                        className={`status-dot ${
                          u.is_active ? "status-dot--active" : "status-dot--disabled"
                        }`}
                      />
                      {u.is_active ? "Active" : "Disabled"}
                    </td>
                    <td>{new Date(u.created_at).toLocaleDateString()}</td>
                    <td>
                      <Link
                        href={`/admin/users/${u.id}`}
                        className="admin-action-link"
                      >
                        Edit
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="pagination-btn"
                disabled={page <= 1}
                onClick={() => setPage((p) => p - 1)}
              >
                Prev
              </button>
              <span className="pagination-info">
                Page {page} of {totalPages}
              </span>
              <button
                className="pagination-btn"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
