"use client";

import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { createClient } from "@/lib/supabase/client";
import { authFetch } from "@/lib/auth-fetch";
import { API_URL } from "@/lib/constants";

const AuthContext = createContext({
  user: null,
  profile: null,
  loading: true,
  signOut: () => {},
  refreshProfile: () => {},
});

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [supabase] = useState(() => createClient());

  const fetchProfile = useCallback(async () => {
    try {
      const res = await authFetch(`${API_URL}/api/auth/me`);
      if (res.ok) {
        setProfile(await res.json());
      } else {
        setProfile(null);
      }
    } catch (err) {
      console.error("Failed to fetch profile:", err);
    }
  }, []);

  useEffect(() => {
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      setUser(session?.user ?? null);
      if (session) {
        await fetchProfile();
      } else {
        setProfile(null);
      }
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, [supabase, fetchProfile]);

  const signOut = async () => {
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
