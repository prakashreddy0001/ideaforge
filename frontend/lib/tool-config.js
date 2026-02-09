export const TOOL_CONFIG = {
  lovable: {
    label: "Lovable",
    url: "https://lovable.dev",
    deepLink: true,
    buildUrl: (prompt) => {
      const encoded = encodeURIComponent(prompt);
      return `https://lovable.dev/?autosubmit=true#prompt=${encoded}`;
    },
    buttonLabel: "Open in Lovable",
    buttonActiveLabel: "Opening Lovable...",
    color: "magenta",
    description: "Opens Lovable and auto-builds your app",
  },
  replit: {
    label: "Replit",
    url: "https://replit.com",
    deepLink: false,
    buildUrl: () => "https://replit.com",
    buttonLabel: "Copy & Open Replit",
    buttonActiveLabel: "Copied! Opening...",
    color: "blue",
    description: "Copies prompt, then opens Replit in a new tab",
  },
  base44: {
    label: "Base44",
    url: "https://www.base44.com",
    deepLink: false,
    buildUrl: () => "https://www.base44.com",
    buttonLabel: "Copy & Open Base44",
    buttonActiveLabel: "Copied! Opening...",
    color: "cyan",
    description: "Copies prompt, then opens Base44 in a new tab",
  },
  claude_code: {
    label: "Claude Code",
    url: null,
    deepLink: false,
    buildUrl: () => null,
    buttonLabel: "Copy for Claude Code",
    buttonActiveLabel: "Copied to clipboard!",
    color: "gold",
    description: "Copies prompt — paste into your Claude Code CLI session",
  },
};

export const TOOL_ORDER = ["lovable", "replit", "base44", "claude_code"];
