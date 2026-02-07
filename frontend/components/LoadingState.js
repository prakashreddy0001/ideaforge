"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { LOADING_MESSAGES } from "@/lib/constants";

export default function LoadingState() {
  const [msgIndex, setMsgIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setMsgIndex((i) => (i + 1) % LOADING_MESSAGES.length);
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="loading-container">
      {/* Typing dots */}
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

      {/* Rotating status text */}
      <AnimatePresence mode="wait">
        <motion.p
          key={msgIndex}
          className="loading-status"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.3 }}
        >
          {LOADING_MESSAGES[msgIndex]}
        </motion.p>
      </AnimatePresence>

      {/* Skeleton bars */}
      <div className="skeleton-group">
        <div className="skeleton-bar" style={{ width: "85%" }} />
        <div className="skeleton-bar" style={{ width: "65%" }} />
        <div className="skeleton-bar" style={{ width: "75%" }} />
        <div className="skeleton-bar" style={{ width: "55%" }} />
      </div>
    </div>
  );
}
