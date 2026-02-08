"use client";

import { useState } from "react";
import AnimatedBackground from "@/components/AnimatedBackground";
import Hero from "@/components/Hero";
import IdeaForm from "@/components/IdeaForm";
import LoadingState from "@/components/LoadingState";
import ResultsSection from "@/components/ResultsSection";
import { useAuth } from "@/components/AuthProvider";
import { createClient } from "@/lib/supabase/client";
import { API_URL } from "@/lib/constants";

export default function GeneratePage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const { user, profile } = useAuth();

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError("");

    try {
      const headers = { "Content-Type": "application/json" };

      const supabase = createClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (session) {
        headers["Authorization"] = `Bearer ${session.access_token}`;
      }

      const res = await fetch(`${API_URL}/api/plan`, {
        method: "POST",
        headers,
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        const payload = await res.json();
        throw new Error(payload.detail || "Failed to generate");
      }

      const payload = await res.json();
      setResult(payload);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <AnimatedBackground />
      <main>
        {user && profile && profile.usage && (
          <div className="usage-indicator">
            <span className={`tier-badge tier-badge--${profile.tier}`}>
              {profile.tier}
            </span>
            {profile.usage.limit !== -1 && (
              <span className="usage-text">
                {profile.usage.used}/{profile.usage.limit} generations used
              </span>
            )}
          </div>
        )}

        <section className="hero">
          <Hero />
          <IdeaForm onSubmit={handleSubmit} loading={loading} />
        </section>

        {error && (
          <p className="error-text" style={{ marginTop: 16 }}>
            {error}
          </p>
        )}

        {loading && <LoadingState />}

        {!loading && result && <ResultsSection result={result} />}
      </main>
    </>
  );
}
