"use client";

import { useState, useCallback } from "react";
import { motion } from "framer-motion";

export default function OpenInToolButton({ prompt, toolConfig }) {
  const [active, setActive] = useState(false);

  const handleClick = useCallback(async () => {
    if (active) return;

    const { deepLink, buildUrl, url } = toolConfig;

    if (deepLink) {
      const deepUrl = buildUrl(prompt);
      if (deepUrl.length > 45000) {
        // Fallback: copy + open without pre-fill
        try { await navigator.clipboard.writeText(prompt); } catch {}
        if (url) window.open(url, "_blank", "noopener,noreferrer");
      } else {
        window.open(deepUrl, "_blank", "noopener,noreferrer");
      }
      setActive(true);
      setTimeout(() => setActive(false), 3000);
      return;
    }

    // Copy & Open: open tab synchronously first (avoids popup blockers)
    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
    }

    try {
      await navigator.clipboard.writeText(prompt);
    } catch {
      /* clipboard may be blocked */
    }

    setActive(true);
    setTimeout(() => setActive(false), 3000);
  }, [prompt, toolConfig, active]);

  return (
    <motion.button
      className={`open-in-tool-btn open-in-tool-btn--${toolConfig.color} ${active ? "open-in-tool-btn--active" : ""}`}
      onClick={handleClick}
      type="button"
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.97 }}
    >
      <span className="open-in-tool-btn-label">
        {active ? toolConfig.buttonActiveLabel : toolConfig.buttonLabel}
      </span>
      {!toolConfig.url && active && (
        <span className="open-in-tool-btn-hint">
          Run: claude in your terminal
        </span>
      )}
    </motion.button>
  );
}
