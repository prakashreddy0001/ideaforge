import { createClient } from "@/lib/supabase/client";

// No module-level singleton — createBrowserClient already returns a
// singleton so calling createClient() always gives the same instance
// that AuthProvider uses.  A separate `_supabase` variable could drift
// after HMR or if the module re-executes.

/**
 * Get a fresh access token, proactively refreshing if expired or about to expire.
 * Returns null if no session exists.
 */
async function getAccessToken() {
  const supabase = createClient();

  const {
    data: { session },
    error,
  } = await supabase.auth.getSession();

  if (error || !session) return null;

  // If the token is already expired OR will expire within 60 s → refresh
  const now = Math.floor(Date.now() / 1000);
  if (session.expires_at && session.expires_at - now < 60) {
    const {
      data: { session: refreshed },
      error: refreshError,
    } = await supabase.auth.refreshSession();

    if (refreshError || !refreshed) return null;
    return refreshed.access_token;
  }

  return session.access_token;
}

/**
 * Fetch wrapper that automatically attaches a fresh Bearer token
 * and retries once on 401 (expired token mid-flight).
 */
export async function authFetch(url, options = {}) {
  const token = await getAccessToken();

  const headers = { ...options.headers };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let res = await fetch(url, { ...options, headers });

  // If 401, force a full token refresh and retry once
  if (res.status === 401) {
    const supabase = createClient();
    const {
      data: { session: refreshed },
    } = await supabase.auth.refreshSession();

    if (refreshed?.access_token) {
      headers["Authorization"] = `Bearer ${refreshed.access_token}`;
      res = await fetch(url, { ...options, headers });
    }
  }

  return res;
}
