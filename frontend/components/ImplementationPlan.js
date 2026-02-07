"use client";

import GlassCard from "./GlassCard";

export default function ImplementationPlan({ steps }) {
  return (
    <GlassCard glowColor="purple">
      <span className="badge">Implementation plan</span>
      <ul className="plan-list">
        {steps.map((step, idx) => {
          const isPhase = step.startsWith("Phase ");
          return (
            <li key={idx} className={isPhase ? "phase-header" : undefined}>
              {step}
            </li>
          );
        })}
      </ul>
    </GlassCard>
  );
}
