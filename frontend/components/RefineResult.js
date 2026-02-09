"use client";

import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import GlassCard from "./GlassCard";
import Accordion from "./Accordion";

const container = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.12, delayChildren: 0.05 },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] },
  },
};

const TYPE_LABELS = {
  code_fix: "Code Fix",
  code_feature: "New Feature",
  code_refactor: "Refactor",
  writing: "Writing",
  design: "Design",
  analysis: "Analysis",
  business: "Business",
  other: "General",
};

export default function RefineResult({ result }) {
  const [copied, setCopied] = useState(false);

  const copyPrompt = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(result.refined_prompt);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard may be blocked */
    }
  }, [result.refined_prompt]);

  return (
    <motion.section
      className="results-section"
      variants={container}
      initial="hidden"
      animate="visible"
    >
      {/* Type + Analysis */}
      <motion.div variants={item}>
        <GlassCard glowColor="cyan" animate={false}>
          <div className="refine-analysis-header">
            <span className="refine-type-badge">
              {TYPE_LABELS[result.prompt_type] || result.prompt_type}
            </span>
            <span className="form-label" style={{ margin: 0 }}>
              Analysis
            </span>
          </div>
          <p className="refine-analysis-text">{result.analysis}</p>
        </GlassCard>
      </motion.div>

      {/* Refined Prompt — main output */}
      <motion.div variants={item}>
        <GlassCard glowColor="gold" animate={false}>
          <span className="master-prompt-badge">Refined Prompt</span>
          <p className="master-prompt-hint">
            This structured prompt is ready to paste into any AI assistant for
            precise, high-quality results.
          </p>

          <motion.button
            className={`master-prompt-copy ${copied ? "copied" : ""}`}
            onClick={copyPrompt}
            type="button"
            whileTap={{ scale: 0.95 }}
          >
            {copied ? "Copied to clipboard!" : "Copy refined prompt"}
          </motion.button>

          <Accordion title="View full prompt" defaultOpen>
            <div className="prompt-block">
              <pre>{result.refined_prompt}</pre>
            </div>
          </Accordion>
        </GlassCard>
      </motion.div>

      {/* Tips */}
      {result.tips && result.tips.length > 0 && (
        <motion.div variants={item}>
          <GlassCard glowColor="purple" animate={false}>
            <span className="form-label">Tips for even better results</span>
            <ul className="refine-tips-list">
              {result.tips.map((tip, i) => (
                <li key={i}>{tip}</li>
              ))}
            </ul>
          </GlassCard>
        </motion.div>
      )}
    </motion.section>
  );
}
