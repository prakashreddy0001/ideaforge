"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const MESSAGES = [
  "Analyzing your prompt...",
  "Identifying intent and context...",
  "Structuring for precision...",
  "Polishing the final prompt...",
];

export default function RefineLoadingState() {
  const [msgIndex, setMsgIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMsgIndex((i) => (i + 1) % MESSAGES.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-container">
      <div className="typing-dots">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="typing-dot"
            animate={{
              opacity: [0.2, 1, 0.2],
              scale: [0.8, 1, 0.8],
            }}
            transition={{
              duration: 1.2,
              repeat: Infinity,
              delay: i * 0.15,
              ease: "easeInOut",
            }}
          />
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.p
          key={msgIndex}
          className="loading-status"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.3 }}
        >
          {MESSAGES[msgIndex]}
        </motion.p>
      </AnimatePresence>

      <div className="skeleton-group">
        <div className="skeleton-bar" style={{ width: "85%" }} />
        <div className="skeleton-bar" style={{ width: "65%" }} />
        <div className="skeleton-bar" style={{ width: "75%" }} />
      </div>
    </div>
  );
}
