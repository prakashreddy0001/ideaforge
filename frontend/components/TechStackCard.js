"use client";

import GlassCard from "./GlassCard";

export default function TechStackCard({ stack }) {
  const entries = Object.entries(stack).filter(([, v]) => v !== "None");

  return (
    <GlassCard glowColor="blue">
      <span className="badge">Tech stack</span>
      <div className="tech-stack-grid">
        {entries.map(([key, value]) => (
          <div key={key} className="tech-stack-item">
            <div className="tech-stack-key">{key.replace(/_/g, " ")}</div>
            <div className="tech-stack-value">{value}</div>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}
