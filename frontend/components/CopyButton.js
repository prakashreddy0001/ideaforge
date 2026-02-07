"use client";

import { useState, useCallback } from "react";
import { motion } from "framer-motion";

export default function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);

  const copy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* clipboard may be blocked */
    }
  }, [text]);

  return (
    <motion.button
      className={`copy-btn ${copied ? "copied" : ""}`}
      onClick={copy}
      type="button"
      whileTap={{ scale: 0.9 }}
    >
      {copied ? "Copied!" : "Copy"}
    </motion.button>
  );
}
