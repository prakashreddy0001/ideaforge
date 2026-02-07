"use client";

import { motion } from "framer-motion";

export default function AnimatedBackground() {
  return (
    <div className="animated-bg">
      <motion.div
        className="orb orb-purple"
        animate={{
          x: [0, 100, -50, 0],
          y: [0, -80, 60, 0],
          scale: [1, 1.1, 0.9, 1],
        }}
        transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
        style={{ top: "10%", left: "15%" }}
      />
      <motion.div
        className="orb orb-blue"
        animate={{
          x: [0, -70, 90, 0],
          y: [0, 50, -60, 0],
          scale: [1, 0.95, 1.05, 1],
        }}
        transition={{ duration: 25, repeat: Infinity, ease: "linear" }}
        style={{ top: "50%", right: "10%" }}
      />
      <motion.div
        className="orb orb-cyan"
        animate={{
          x: [0, 60, -40, 0],
          y: [0, -40, 80, 0],
          scale: [1, 1.08, 0.92, 1],
        }}
        transition={{ duration: 18, repeat: Infinity, ease: "linear" }}
        style={{ bottom: "15%", left: "40%" }}
      />
    </div>
  );
}
