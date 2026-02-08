"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import AnimatedBackground from "@/components/AnimatedBackground";
import { useAuth } from "@/components/AuthProvider";

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.1, ease: [0.16, 1, 0.3, 1] },
  }),
};

const FEATURES = [
  {
    title: "Smart Stack Selection",
    desc: "AI analyzes your idea and picks the optimal tech stack — frontend, backend, database, hosting, and more.",
    glow: "purple",
  },
  {
    title: "Code-Gen Prompts",
    desc: "Get 9-15 heavy, production-ready prompts tailored to your stack and domain. Copy-paste into any AI coding tool.",
    glow: "blue",
  },
  {
    title: "Domain Analysis",
    desc: "Automatic extraction of entities, API endpoints, pages, and workflows specific to your product domain.",
    glow: "cyan",
  },
  {
    title: "Full Documentation",
    desc: "PRD, technical architecture, API specs, database schema, and deployment guides — generated automatically.",
    glow: "purple",
  },
  {
    title: "Implementation Plan",
    desc: "A phased roadmap from foundation to launch, with clear milestones and deliverables for each phase.",
    glow: "blue",
  },
  {
    title: "Multi-Tool Support",
    desc: "Prompts optimized for Lovable, Replit, Claude Code, Base44, or auto-detected best-fit tools.",
    glow: "cyan",
  },
];

const STEPS = [
  {
    num: "01",
    title: "Describe Your Idea",
    desc: "Drop in a product idea in plain English. Add target users and budget for better results.",
  },
  {
    num: "02",
    title: "AI Analyzes & Plans",
    desc: "IdeaForge detects features, selects the tech stack, and builds a domain model for your product.",
  },
  {
    num: "03",
    title: "Get Your Build Package",
    desc: "Receive code-gen prompts, documentation, implementation plan, and a master prompt — ready to build.",
  },
];

export default function LandingPage() {
  const { user } = useAuth();

  return (
    <>
      <AnimatedBackground />
      <main className="landing">
        {/* ── Hero ── */}
        <section className="landing-hero">
          <motion.div
            className="landing-hero-content"
            initial="hidden"
            animate="visible"
          >
            <motion.span className="kicker" custom={0} variants={fadeUp}>
              AI-Powered Build Packages
            </motion.span>
            <motion.h1 className="landing-hero-title" custom={1} variants={fadeUp}>
              Turn a rough idea into a
              <span className="landing-gradient-text"> build-ready package</span>
            </motion.h1>
            <motion.p className="landing-hero-desc" custom={2} variants={fadeUp}>
              Drop in a product idea and get an implementation roadmap, optimized
              tech stack, heavy code-generation prompts, and tailored docs — all
              in one pass.
            </motion.p>
            <motion.div className="landing-hero-actions" custom={3} variants={fadeUp}>
              <Link href={user ? "/generate" : "/register"} className="neon-btn landing-cta-primary">
                Start Building
              </Link>
              <Link href="/pricing" className="landing-cta-secondary">
                View Plans
              </Link>
            </motion.div>
            <motion.p className="landing-hero-note" custom={4} variants={fadeUp}>
              Free tier includes 5 generations per month
            </motion.p>
          </motion.div>

          <motion.div
            className="landing-hero-visual"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
          >
            <div className="landing-preview glass-card">
              <div className="landing-preview-header">
                <span className="landing-preview-dot" style={{ background: "#ec4899" }} />
                <span className="landing-preview-dot" style={{ background: "#f59e0b" }} />
                <span className="landing-preview-dot" style={{ background: "#10b981" }} />
                <span className="landing-preview-title">IdeaForge Output</span>
              </div>
              <div className="landing-preview-body">
                <div className="landing-preview-line landing-preview-line--accent">
                  <span className="landing-preview-label">Stack</span>
                  <span>Next.js + FastAPI + PostgreSQL</span>
                </div>
                <div className="landing-preview-line">
                  <span className="landing-preview-label">Prompts</span>
                  <span>12 code-gen prompts generated</span>
                </div>
                <div className="landing-preview-line">
                  <span className="landing-preview-label">Docs</span>
                  <span>PRD, API spec, DB schema, deploy guide</span>
                </div>
                <div className="landing-preview-line">
                  <span className="landing-preview-label">Plan</span>
                  <span>5-phase implementation roadmap</span>
                </div>
                <div className="landing-preview-line landing-preview-line--gold">
                  <span className="landing-preview-label">Master</span>
                  <span>Single mega-prompt ready</span>
                </div>
              </div>
            </div>
          </motion.div>
        </section>

        {/* ── Features ── */}
        <section className="landing-section">
          <div className="landing-section-header">
            <h2 className="landing-section-title">Everything you need to start building</h2>
            <p className="landing-section-desc">
              From idea to architecture to code-ready prompts — IdeaForge handles the heavy lifting.
            </p>
          </div>

          <div className="landing-features-grid">
            {FEATURES.map((f, i) => (
              <motion.div
                key={f.title}
                className={`glass-card landing-feature-card glass-card--glow-${f.glow}`}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
              >
                <h3 className="landing-feature-title">{f.title}</h3>
                <p className="landing-feature-desc">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </section>

        {/* ── How It Works ── */}
        <section className="landing-section">
          <div className="landing-section-header">
            <h2 className="landing-section-title">How it works</h2>
            <p className="landing-section-desc">
              Three steps from idea to build-ready package.
            </p>
          </div>

          <div className="landing-steps">
            {STEPS.map((s, i) => (
              <motion.div
                key={s.num}
                className="landing-step"
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: i * 0.15 }}
              >
                <span className="landing-step-num">{s.num}</span>
                <div>
                  <h3 className="landing-step-title">{s.title}</h3>
                  <p className="landing-step-desc">{s.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </section>

        {/* ── CTA ── */}
        <section className="landing-section landing-cta-section">
          <motion.div
            className="glass-card landing-cta-card"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="landing-cta-title">Ready to build something?</h2>
            <p className="landing-cta-desc">
              Stop planning in your head. Get a structured build package in minutes.
            </p>
            <Link href={user ? "/generate" : "/register"} className="neon-btn landing-cta-primary">
              Get Started Free
            </Link>
          </motion.div>
        </section>
      </main>
    </>
  );
}
