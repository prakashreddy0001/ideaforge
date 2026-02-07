"use client";

import { motion } from "framer-motion";

export default function FeatureBadge({ name }) {
  return (
    <motion.span
      className="feature-badge"
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: "spring", stiffness: 400, damping: 20 }}
    >
      {name.replace(/_/g, " ")}
    </motion.span>
  );
}
