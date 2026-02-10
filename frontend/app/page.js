import HomeContent from "./HomeContent";
import { JsonLd } from "@/components/JsonLd";

export const metadata = {
  title: "IdeaForge — Turn Ideas into Build-Ready Packages",
  description:
    "Transform any product idea into an optimized tech stack, code-gen prompts, documentation, and a phased implementation plan.",
  alternates: {
    canonical: "/",
  },
};

export default function HomePage() {
  return (
    <>
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "SoftwareApplication",
          name: "IdeaForge",
          applicationCategory: "DeveloperApplication",
          operatingSystem: "Web",
          description:
            "AI-powered platform that transforms product ideas into build-ready packages with tech stack, code prompts, docs, and plans.",
          offers: {
            "@type": "Offer",
            price: "0",
            priceCurrency: "USD",
          },
        }}
      />
      <HomeContent />
    </>
  );
}
