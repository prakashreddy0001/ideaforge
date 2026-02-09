"use client";

import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import GlassCard from "./GlassCard";
import Accordion from "./Accordion";
import OpenInToolButton from "./OpenInToolButton";
import { TOOL_CONFIG, TOOL_ORDER } from "@/lib/tool-config";

export default function MasterPromptCard({ prompt, tool }) {
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

  const toolsToShow =
    tool && TOOL_CONFIG[tool] ? [tool] : TOOL_ORDER;

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

      <div
        className={`open-in-tool-section ${toolsToShow.length > 1 ? "open-in-tool-section--grid" : ""}`}
      >
        {toolsToShow.map((slug) => (
          <OpenInToolButton
            key={slug}
            prompt={prompt}
            toolConfig={TOOL_CONFIG[slug]}
          />
        ))}
      </div>

      <Accordion title="View full prompt" defaultOpen={false}>
        <div className="prompt-block">
          <pre>{prompt}</pre>
        </div>
      </Accordion>
    </GlassCard>
  );
}
