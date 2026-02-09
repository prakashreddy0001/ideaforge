"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { createClient } from "@/lib/supabase/client";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams.get("redirect") || "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    const supabase = createClient();
    const { error: authError } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (authError) {
      setError(authError.message);
      setLoading(false);
      return;
    }

    router.push(redirect);
    router.refresh();
  };

  return (
    <div className="auth-card glass-card">
      <h1 className="auth-title">Welcome back</h1>
      <p className="auth-subtitle">Sign in to your IdeaForge account</p>

      <form onSubmit={handleSubmit} className="auth-form">
        <label className="form-label" htmlFor="email">
          Email
        </label>
        <input
          id="email"
          type="email"
          className="input auth-input"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <label className="form-label" htmlFor="password">
          Password
        </label>
        <input
          id="password"
          type="password"
          className="input auth-input"
          placeholder="Your password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        {error && <p className="error-text">{error}</p>}

        <button type="submit" className="neon-btn auth-submit" disabled={loading}>
          {loading ? "Signing in..." : "Sign In"}
        </button>
      </form>

      <p className="auth-footer">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="auth-link">
          Sign up
        </Link>
      </p>
    </div>
  );
}

export default function LoginPage() {
  return (
    <main className="auth-page">
      <Suspense fallback={<div className="auth-card glass-card"><p>Loading...</p></div>}>
        <LoginForm />
      </Suspense>
    </main>
  );
}
