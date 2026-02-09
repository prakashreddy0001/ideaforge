"use client";

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/cjs/styles/prism";
import GlassCard from "./GlassCard";
import CopyButton from "./CopyButton";

const LANG_MAP = {
  jsx: "jsx",
  html: "markup",
};

export default function DesignCodeResult({ result }) {
  const lang = LANG_MAP[result.language] || result.language;

  return (
    <GlassCard glowColor="cyan">
      <div className="card-header-row">
        <span className="badge badge--cyan">{result.format_label}</span>
      </div>
      <p className="card-hint">
        Generated code from your design. Copy and paste into your project.
      </p>
      <div className="code-result-block">
        <div className="code-result-copy">
          <CopyButton text={result.code} />
        </div>
        <SyntaxHighlighter
          language={lang}
          style={vscDarkPlus}
          showLineNumbers
          customStyle={{
            background: "rgba(0, 0, 0, 0.4)",
            border: "1px solid rgba(255, 255, 255, 0.08)",
            borderRadius: "12px",
            padding: "16px",
            fontSize: "13px",
            fontFamily: "var(--font-mono, 'JetBrains Mono', monospace)",
            margin: 0,
            maxHeight: "600px",
            overflow: "auto",
          }}
          lineNumberStyle={{
            color: "rgba(255, 255, 255, 0.2)",
            fontSize: "12px",
            paddingRight: "16px",
          }}
        >
          {result.code}
        </SyntaxHighlighter>
      </div>
    </GlassCard>
  );
}
