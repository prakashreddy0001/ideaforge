import { ImageResponse } from "next/og";

export const runtime = "edge";

export const alt = "IdeaForge — Turn Ideas into Build-Ready Packages";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OgImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #0a0a0f 0%, #1a1025 50%, #0a0a0f 100%)",
          fontFamily: "system-ui, sans-serif",
        }}
      >
        {/* Lightning bolt icon */}
        <svg
          width="80"
          height="80"
          viewBox="0 0 32 32"
          style={{ marginBottom: 24 }}
        >
          <rect width="32" height="32" rx="8" fill="#1a1025" />
          <path d="M17 4L7 18h7l-1 10L23 14h-7l1-10z" fill="#a855f7" />
        </svg>

        <div
          style={{
            fontSize: 64,
            fontWeight: 700,
            color: "#ffffff",
            marginBottom: 16,
            display: "flex",
          }}
        >
          IdeaForge
        </div>

        <div
          style={{
            fontSize: 28,
            color: "#a1a1aa",
            textAlign: "center",
            maxWidth: 700,
            lineHeight: 1.4,
            display: "flex",
          }}
        >
          Turn a rough idea into a build-ready package
        </div>

        <div
          style={{
            display: "flex",
            gap: 32,
            marginTop: 40,
          }}
        >
          {["Tech Stack", "Code Prompts", "Documentation", "Implementation Plan"].map(
            (item) => (
              <div
                key={item}
                style={{
                  fontSize: 18,
                  color: "#a855f7",
                  padding: "8px 20px",
                  border: "1px solid #a855f740",
                  borderRadius: 8,
                  display: "flex",
                }}
              >
                {item}
              </div>
            )
          )}
        </div>
      </div>
    ),
    { ...size }
  );
}
