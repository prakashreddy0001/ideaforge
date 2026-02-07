"use client";

import GlassCard from "./GlassCard";
import Accordion from "./Accordion";
import CopyButton from "./CopyButton";

export default function PromptPackCard({ prompts }) {
  const entries = Object.entries(prompts);

  return (
    <GlassCard glowColor="purple">
      <span className="badge">Prompt pack ({entries.length})</span>
      <p className="card-hint">
        Each prompt is self-contained — copy it into any AI code assistant to
        generate that section of your application.
      </p>
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
