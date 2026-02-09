"use client";

export default function Error({ error, reset }) {
  return (
    <main className="auth-page">
      <div className="glass-card" style={{ padding: "2rem", textAlign: "center", maxWidth: 480, margin: "0 auto" }}>
        <h2 style={{ marginBottom: "0.5rem" }}>Something went wrong</h2>
        <p className="error-text" style={{ marginBottom: "1rem" }}>
          {error?.message || "An unexpected error occurred."}
        </p>
        <button onClick={reset} className="neon-btn">
          Try Again
        </button>
      </div>
    </main>
  );
}
