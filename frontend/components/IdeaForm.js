"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import NeonButton from "./NeonButton";
import {
  DEFAULT_IDEA,
  DEFAULT_TARGET_USERS,
  DEFAULT_BUDGET,
} from "@/lib/constants";

const TOOLS = [
  { slug: null, label: "Default", desc: "Auto-detected stack" },
  { slug: "lovable", label: "Lovable", desc: "React + Supabase" },
  { slug: "replit", label: "Replit", desc: "Express + React" },
  { slug: "base44", label: "Base44", desc: "No-code platform" },
  { slug: "claude_code", label: "Claude Code", desc: "Full code-gen" },
];

export default function IdeaForm({ onSubmit, loading }) {
  const [idea, setIdea] = useState(DEFAULT_IDEA);
  const [targetUsers, setTargetUsers] = useState(DEFAULT_TARGET_USERS);
  const [budget, setBudget] = useState(DEFAULT_BUDGET);
  const [mode, setMode] = useState("production");
  const [tool, setTool] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ idea, target_users: targetUsers, budget, mode, tool });
  };

  const selectedTool = TOOLS.find((t) => t.slug === tool);

  return (
    <motion.div
      className="panel"
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
    >
      <form onSubmit={handleSubmit}>
        <label className="form-label">Your idea</label>
        <textarea
          className="idea-input"
          value={idea}
          onChange={(e) => setIdea(e.target.value)}
          placeholder="Describe your product idea..."
        />

        <div className="row">
          <input
            className="input"
            value={targetUsers}
            onChange={(e) => setTargetUsers(e.target.value)}
            placeholder="Target users"
          />
          <input
            className="input"
            value={budget}
            onChange={(e) => setBudget(e.target.value)}
            placeholder="Budget"
          />
        </div>

        <label className="form-label" style={{ marginTop: 16 }}>
          AI coding tool
        </label>
        <div className="tool-selector">
          {TOOLS.map((t) => (
            <button
              key={t.slug ?? "default"}
              type="button"
              className={`tool-card ${tool === t.slug ? "tool-card--active" : ""}`}
              onClick={() => setTool(t.slug)}
            >
              <span className="tool-card-label">{t.label}</span>
              <span className="tool-card-desc">{t.desc}</span>
            </button>
          ))}
        </div>
        <p className="mode-hint">
          {selectedTool && selectedTool.slug
            ? `Prompts tailored for ${selectedTool.label}`
            : "Prompts use auto-detected best stack"}
        </p>

        <div className="mode-toggle">
          <button
            type="button"
            className={`mode-pill ${mode === "mvp" ? "active" : ""}`}
            onClick={() => setMode("mvp")}
          >
            MVP
          </button>
          <button
            type="button"
            className={`mode-pill ${mode === "production" ? "active" : ""}`}
            onClick={() => setMode("production")}
          >
            Production
          </button>
        </div>
        <p className="mode-hint">
          {mode === "mvp"
            ? "3 essential prompts for rapid prototyping"
            : "9-15 comprehensive prompts for production-grade code"}
        </p>

        <div className="row" style={{ marginTop: 10 }}>
          <NeonButton type="submit" disabled={loading}>
            {loading ? "Generating..." : "Generate package"}
          </NeonButton>
        </div>
      </form>
    </motion.div>
  );
}
