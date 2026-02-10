import PricingContent from "./PricingContent";
import { JsonLd } from "@/components/JsonLd";

export const metadata = {
  title: "Pricing",
  description:
    "Choose the right IdeaForge plan. Free tier with 5 generations/month, Pro at $19/mo with 50 generations, or Enterprise at $49/mo unlimited.",
  alternates: {
    canonical: "/pricing",
  },
};

export default function PricingPage() {
  return (
    <>
      <JsonLd
        data={{
          "@context": "https://schema.org",
          "@type": "Product",
          name: "IdeaForge",
          description: "AI-powered idea-to-build-package platform",
          offers: [
            {
              "@type": "Offer",
              name: "Free",
              price: "0",
              priceCurrency: "USD",
              description: "5 generations per month, MVP mode",
            },
            {
              "@type": "Offer",
              name: "Pro",
              price: "19",
              priceCurrency: "USD",
              description: "50 generations per month, all modes and tools",
            },
            {
              "@type": "Offer",
              name: "Enterprise",
              price: "49",
              priceCurrency: "USD",
              description: "Unlimited generations, priority support",
            },
          ],
        }}
      />
      <PricingContent />
    </>
  );
}
