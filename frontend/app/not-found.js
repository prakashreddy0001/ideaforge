import Link from "next/link";

export default function NotFound() {
  return (
    <main className="auth-page">
      <div className="glass-card" style={{ padding: "2rem", textAlign: "center", maxWidth: 480, margin: "0 auto" }}>
        <h2 style={{ marginBottom: "0.5rem" }}>Page Not Found</h2>
        <p style={{ marginBottom: "1rem", opacity: 0.7 }}>
          The page you are looking for does not exist.
        </p>
        <Link href="/" className="neon-btn">
          Go Home
        </Link>
      </div>
    </main>
  );
}
