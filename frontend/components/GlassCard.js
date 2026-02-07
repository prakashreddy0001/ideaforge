"use client";

import { motion } from "framer-motion";

export default function GlassCard({
  children,
  className = "",
  glowColor = "",
  animate = true,
}) {
  const glowClass = glowColor ? `glass-card--glow-${glowColor}` : "";
  const classes = `glass-card ${glowClass} ${className}`.trim();

  if (!animate) {
    return <div className={classes}>{children}</div>;
  }

  return (
    <motion.div
      className={classes}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </motion.div>
  );
}
