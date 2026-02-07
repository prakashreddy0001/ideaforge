"use client";

import { motion } from "framer-motion";
import FeatureBadge from "./FeatureBadge";

export default function MetaBar({ result }) {
  if (!result.detected_features && !result.estimated_complexity) return null;

  return (
    <motion.div
      className="meta-bar"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
    >
      {result.estimated_complexity && (
        <span className="complexity-badge">{result.estimated_complexity}</span>
      )}
      {result.prompt_count && (
        <span className="prompt-count">
          {result.prompt_count} prompts generated
        </span>
      )}
      {result.detected_features &&
        result.detected_features.map((f) => (
          <FeatureBadge key={f} name={f} />
        ))}
    </motion.div>
  );
}
