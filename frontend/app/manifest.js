export default function manifest() {
  return {
    name: "IdeaForge",
    short_name: "IdeaForge",
    description:
      "Turn a rough idea into a build-ready package — stack, prompts, docs, and plan.",
    start_url: "/",
    display: "standalone",
    background_color: "#0a0a0f",
    theme_color: "#0a0a0f",
    icons: [
      {
        src: "/icon.svg",
        sizes: "any",
        type: "image/svg+xml",
      },
    ],
  };
}
