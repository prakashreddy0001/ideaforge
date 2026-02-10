"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import AnimatedBackground from "@/components/AnimatedBackground";
import RefineForm from "@/components/RefineForm";
import RefineLoadingState from "@/components/RefineLoadingState";
import RefineResult from "@/components/RefineResult";
import { useAuth } from "@/components/AuthProvider";
import { authFetch } from "@/lib/auth-fetch";
import { API_URL } from "@/lib/constants";

export default function RefineContent() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const { user, profile, loading: authLoading } = useAuth();
  const router = useRouter();

  if (authLoading) {
    return (
      <main>
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

  const handleSubmit = async (prompt) => {
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const res = await authFetch(`${API_URL}/api/refine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });

      if (!res.ok) {
        const payload = await res.json();
        throw new Error(payload.detail || "Failed to refine prompt");
      }

      setResult(await res.json());
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

        <section className="refine-hero">
          <motion.div
            className="refine-hero-content"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          >
            <h1 className="refine-title">Prompt Refiner</h1>
            <p className="refine-subtitle">
              Paste any vague prompt and get back a structured, precise one-shot
              prompt that any AI will execute with 95%+ accuracy.
            </p>
          </motion.div>
          <RefineForm onSubmit={handleSubmit} loading={loading} />
        </section>

        {error && (
          <p className="error-text" style={{ marginTop: 16 }}>
            {error}
          </p>
        )}

        {loading && <RefineLoadingState />}

        {!loading && result && <RefineResult result={result} />}
      </main>
    </>
  );
}
