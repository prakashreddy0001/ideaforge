"use client";

import GlassCard from "./GlassCard";
import Accordion from "./Accordion";
import CopyButton from "./CopyButton";

export default function DocsCard({ docs }) {
  const entries = Object.entries(docs);

  return (
    <GlassCard glowColor="cyan">
      <span className="badge refined-badge">Docs ({entries.length})</span>
      {entries.map(([key, value]) => (
        <Accordion key={key} title={key.replace(/_/g, " ")}>
          <div className="prompt-block">
            <CopyButton text={value} />
            <pre>{value}</pre>
          </div>
        </Accordion>
      ))}
    </GlassCard>
  );
}
