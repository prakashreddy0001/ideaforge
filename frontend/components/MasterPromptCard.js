"use client";

import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import GlassCard from "./GlassCard";
import Accordion from "./Accordion";

export default function MasterPromptCard({ prompt }) {
  const [copied, setCopied] = useState(false);

  const copy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(prompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard may be blocked */
    }
  }, [prompt]);

  return (
    <GlassCard glowColor="gold">
      <span className="master-prompt-badge">Master Prompt</span>
      <p className="master-prompt-hint">
        This single prompt contains everything — paste it into any AI coding
        assistant to build your entire application in one go.
      </p>

      <motion.button
        className={`master-prompt-copy ${copied ? "copied" : ""}`}
        onClick={copy}
        type="button"
        whileTap={{ scale: 0.95 }}
      >
        {copied ? "Copied to clipboard!" : "Copy master prompt"}
      </motion.button>

      <Accordion title="View full prompt" defaultOpen={false}>
        <div className="prompt-block">
          <pre>{prompt}</pre>
        </div>
      </Accordion>
    </GlassCard>
  );
}
