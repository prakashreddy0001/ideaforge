"use client";

import { createContext, useContext, useEffect, useState, useCallback, useRef } from "react";
import { createClient } from "@/lib/supabase/client";
import { authFetch } from "@/lib/auth-fetch";
import { API_URL } from "@/lib/constants";

const AuthContext = createContext({
  user: null,
  profile: null,
  loading: true,
  signOut: () => {},
  refreshProfile: () => {},
  supabase: null,
});

const SESSION_KEY = "ideaforge-auth";

/** Persist tokens so the session survives a page refresh even when
 *  Supabase's cookie-based storage fails to re-hydrate. */
function cacheSession(session) {
  try {
    sessionStorage.setItem(
      SESSION_KEY,
      JSON.stringify({
        access_token: session.access_token,
        refresh_token: session.refresh_token,
      })
    );
  } catch {}
}

function clearCachedSession() {
  try {
    sessionStorage.removeItem(SESSION_KEY);
  } catch {}
}

function getCachedSession() {
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (parsed?.access_token && parsed?.refresh_token) return parsed;
  } catch {}
  return null;
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [supabase] = useState(() => createClient());
  const fetchingRef = useRef(false);

  const fetchProfile = useCallback(async () => {
    if (fetchingRef.current) return;
    fetchingRef.current = true;
    try {
      const res = await authFetch(`${API_URL}/api/auth/me`);
      if (res.ok) {
        setProfile(await res.json());
      } else {
        setProfile(null);
      }
    } catch (err) {
      console.error("Failed to fetch profile:", err);
      setProfile(null);
    } finally {
      fetchingRef.current = false;
    }
  }, []);

  useEffect(() => {
    let mounted = true;
    let sub;

    async function init() {
      // ── 1. Restore session from sessionStorage on mount ──
      // This is the PRIMARY path — do not rely on Supabase's
      // cookie-based re-hydration which can silently fail.
      const cached = getCachedSession();
      if (cached) {
        const { data } = await supabase.auth.setSession({
          access_token: cached.access_token,
          refresh_token: cached.refresh_token,
        });
        if (!mounted) return;
        if (data?.session) {
          cacheSession(data.session);
          setUser(data.session.user);
          await fetchProfile();
        } else {
          clearCachedSession();
        }
      }
      if (mounted) setLoading(false);

      // ── 2. Listen for future auth events ─────────────────
      // Skip INITIAL_SESSION — init() above already handled it.
      const { data: { subscription } } = supabase.auth.onAuthStateChange(
        async (event, session) => {
          if (!mounted || event === "INITIAL_SESSION") return;

          if (event === "SIGNED_OUT") {
            clearCachedSession();
            setUser(null);
            setProfile(null);
            return;
          }

          if (session) {
            cacheSession(session);
            setUser(session.user);
            if (event !== "TOKEN_REFRESHED") {
              await fetchProfile();
            }
          }
        }
      );
      sub = subscription;
    }

    init();

    // Re-validate when the tab regains focus.
    const handleVisibility = () => {
      if (document.visibilityState === "visible") {
        const cached = getCachedSession();
        if (cached) {
          supabase.auth.setSession({
            access_token: cached.access_token,
            refresh_token: cached.refresh_token,
          }).then(({ data }) => {
            if (!mounted) return;
            if (data?.session) {
              cacheSession(data.session);
              setUser(data.session.user);
              fetchProfile();
            }
          });
        }
      }
    };
    document.addEventListener("visibilitychange", handleVisibility);

    return () => {
      mounted = false;
      sub?.unsubscribe();
      document.removeEventListener("visibilitychange", handleVisibility);
    };
  }, [supabase, fetchProfile]);

  const signOut = async () => {
    clearCachedSession();
    await supabase.auth.signOut();
    setUser(null);
    setProfile(null);
  };

  const refreshProfile = async () => {
    await fetchProfile();
  };

  return (
    <AuthContext.Provider
      value={{ user, profile, loading, signOut, refreshProfile, supabase }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
