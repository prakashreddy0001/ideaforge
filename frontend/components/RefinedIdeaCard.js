"use client";

import GlassCard from "./GlassCard";

export default function RefinedIdeaCard({ refinedIdea }) {
  if (!refinedIdea) return null;

  return (
    <GlassCard className="refined-card" glowColor="cyan">
      <span className="badge refined-badge">Refined idea</span>
      <p className="refined-text">{refinedIdea}</p>
    </GlassCard>
  );
}
