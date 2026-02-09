"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import NeonButton from "./NeonButton";

export default function RefineForm({ onSubmit, loading }) {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (prompt.trim().length >= 5) {
      onSubmit(prompt.trim());
    }
  };

  return (
    <motion.div
      className="panel"
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
    >
      <form onSubmit={handleSubmit}>
        <label className="form-label">Your vague prompt</label>
        <textarea
          className="idea-input"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder='Paste any vague or poorly-structured prompt here... e.g. "fix that bug when editing a product" or "write me a cold email for my SaaS"'
          rows={5}
        />
        <p className="mode-hint" style={{ marginTop: 8 }}>
          Works with any type of prompt — code, writing, design, business,
          analysis, and more.
        </p>
        <div className="row" style={{ marginTop: 14 }}>
          <NeonButton type="submit" disabled={loading || prompt.trim().length < 5}>
            {loading ? "Refining..." : "Refine prompt"}
          </NeonButton>
        </div>
      </form>
    </motion.div>
  );
}
