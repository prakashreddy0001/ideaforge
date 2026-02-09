export const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const DEFAULT_IDEA =
  "A habit coaching app that turns journaling into weekly experiments with AI feedback.";

export const DEFAULT_TARGET_USERS = "Busy professionals";

export const DEFAULT_BUDGET = "MVP under $10k";

export const LOADING_MESSAGES = [
  "Analyzing your idea...",
  "Detecting features...",
  "Selecting tech stack...",
  "Generating prompts...",
  "Assembling docs...",
];

export const DESIGN_LOADING_MESSAGES = [
  "Analyzing your design...",
  "Identifying layout structure...",
  "Extracting colors and typography...",
  "Detecting interactive elements...",
  "Generating production-ready code...",
  "Polishing and formatting...",
];
