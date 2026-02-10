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

const TOOLS = [
  {
    title: "Generate",
    desc: "Transform any product idea into a complete build package — optimized tech stack, code-gen prompts, full documentation, and a phased implementation plan.",
    href: "/generate",
    glow: "purple",
    linkText: "Start Generating",
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
      </svg>
    ),
  },
  {
    title: "Refine",
    desc: "Turn vague prompts into precise, actionable instructions. Get deep analysis, improvement tips, and a polished version ready to paste into any AI tool.",
    href: "/refine",
    glow: "cyan",
    linkText: "Try Refiner",
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2L15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2z" />
      </svg>
    ),
  },
  {
    title: "Dashboard",
    desc: "Track your generation usage, manage your subscription, view plan details, and quickly jump back into building from a single command center.",
    href: "/dashboard",
    glow: "blue",
    linkText: "View Dashboard",
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7" />
        <rect x="14" y="3" width="7" height="7" />
        <rect x="14" y="14" width="7" height="7" />
        <rect x="3" y="14" width="7" height="7" />
      </svg>
    ),
  },
];

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

export default function HomeContent() {
  const { user } = useAuth();

  return (
    <>
      <AnimatedBackground />
      <main className="landing">
        {/* ── Hero ── */}
        <section className="landing-hero landing-hero--centered">
          <motion.div
            className="landing-hero-content landing-hero-content--centered"
            initial="hidden"
            animate="visible"
          >
            <motion.span className="kicker" custom={0} variants={fadeUp}>
              AI-Powered Build Packages
            </motion.span>
            <motion.h1 className="landing-hero-title landing-hero-title--centered" custom={1} variants={fadeUp}>
              Turn a rough idea into a
              <span className="landing-gradient-text"> build-ready package</span>
            </motion.h1>
            <motion.p className="landing-hero-desc landing-hero-desc--centered" custom={2} variants={fadeUp}>
              Drop in a product idea and get an implementation roadmap, optimized
              tech stack, heavy code-generation prompts, and tailored docs — all
              in one pass.
            </motion.p>
            <motion.div className="landing-hero-actions landing-hero-actions--centered" custom={3} variants={fadeUp}>
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
            className="landing-hero-visual landing-hero-visual--centered"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
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

        {/* ── Tools Showcase ── */}
        <section className="landing-section">
          <div className="landing-section-header">
            <h2 className="landing-section-title">Powerful Tools</h2>
            <p className="landing-section-desc">
              Everything you need to go from idea to production — all in one platform.
            </p>
          </div>

          <div className="landing-tools-grid">
            {TOOLS.map((tool, i) => (
              <motion.div
                key={tool.title}
                className={`glass-card landing-tool-card glass-card--glow-${tool.glow}`}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
              >
                <div className={`landing-tool-icon landing-tool-icon--${tool.glow}`}>
                  {tool.icon}
                </div>
                <h3 className="landing-tool-title">{tool.title}</h3>
                <p className="landing-tool-desc">{tool.desc}</p>
                <Link href={tool.href} className={`landing-tool-link landing-tool-link--${tool.glow}`}>
                  {tool.linkText}
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="5" y1="12" x2="19" y2="12" />
                    <polyline points="12 5 19 12 12 19" />
                  </svg>
                </Link>
              </motion.div>
            ))}
          </div>
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
