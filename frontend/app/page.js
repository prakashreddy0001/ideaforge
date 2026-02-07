"use client";

import { useState } from "react";
import AnimatedBackground from "@/components/AnimatedBackground";
import Hero from "@/components/Hero";
import IdeaForm from "@/components/IdeaForm";
import LoadingState from "@/components/LoadingState";
import ResultsSection from "@/components/ResultsSection";
import { API_URL } from "@/lib/constants";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async (formData) => {
    setLoading(true);
    setError("");

    try {
      const res = await fetch(`${API_URL}/api/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
        <section className="hero">
          <Hero />
          <IdeaForm onSubmit={handleSubmit} loading={loading} />
        </section>

        {error && (
          <p className="error-text" style={{ marginTop: 16 }}>{error}</p>
        )}

        {loading && <LoadingState />}

        {!loading && result && <ResultsSection result={result} />}
      </main>
    </>
  );
}
