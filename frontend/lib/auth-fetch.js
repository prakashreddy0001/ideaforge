import { createClient } from "@/lib/supabase/client";

let _supabase = null;

function getSupabase() {
  if (!_supabase) {
    _supabase = createClient();
  }
  return _supabase;
}

/**
 * Get a fresh access token, proactively refreshing if expired or about to expire.
 * Returns null if no session exists.
 */
async function getAccessToken() {
  const supabase = getSupabase();

  const {
    data: { session },
    error,
  } = await supabase.auth.getSession();

  if (error || !session) return null;

  // If token expires within 60 seconds, force a refresh
  const now = Math.floor(Date.now() / 1000);
  if (session.expires_at && session.expires_at - now < 60) {
    const {
      data: { session: refreshed },
    } = await supabase.auth.refreshSession();
    return refreshed?.access_token ?? null;
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

  // If 401, try refreshing the token once and retry
  if (res.status === 401) {
    const supabase = getSupabase();
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
