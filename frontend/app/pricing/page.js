"use client";

import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import AnimatedBackground from "@/components/AnimatedBackground";

const TIERS = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    features: [
      "5 generations / month",
      "MVP mode only",
      "Default tool only",
      "2,000 char idea limit",
    ],
    cta: "Get Started",
    tier: "free",
    highlighted: false,
  },
  {
    name: "Pro",
    price: "$19",
    period: "/month",
    features: [
      "50 generations / month",
      "MVP + Production modes",
      "All AI tools",
      "4,000 char idea limit",
    ],
    cta: "Contact Us",
    tier: "pro",
    highlighted: true,
  },
  {
    name: "Enterprise",
    price: "$49",
    period: "/month",
    features: [
      "Unlimited generations",
      "MVP + Production modes",
      "All AI tools + priority",
      "4,000 char idea limit",
      "Priority support",
    ],
    cta: "Contact Us",
    tier: "enterprise",
    highlighted: false,
  },
];

export default function PricingPage() {
  const { user, profile } = useAuth();
  const router = useRouter();

  const handleAction = (tier) => {
    if (!user) {
      router.push("/register");
      return;
    }
    if (tier === "free") {
      router.push("/dashboard");
    }
  };

  return (
    <>
      <AnimatedBackground />
      <main className="pricing-page">
        <div className="pricing-header">
          <h1 className="pricing-title">Choose your plan</h1>
          <p className="pricing-subtitle">
            Start free, upgrade when you need more power.
          </p>
        </div>

        <div className="pricing-grid">
          {TIERS.map((t) => (
            <div
              key={t.tier}
              className={`pricing-card glass-card ${
                t.highlighted ? "pricing-card--highlighted" : ""
              }`}
            >
              {t.highlighted && <span className="pricing-popular">Most Popular</span>}
              <h2 className="pricing-card-name">{t.name}</h2>
              <div className="pricing-card-price">
                <span className="pricing-amount">{t.price}</span>
                <span className="pricing-period">{t.period}</span>
              </div>
              <ul className="pricing-features">
                {t.features.map((f, i) => (
                  <li key={i}>{f}</li>
                ))}
              </ul>
              <button
                className={`neon-btn pricing-cta ${
                  t.highlighted ? "" : "pricing-cta--secondary"
                }`}
                onClick={() => handleAction(t.tier)}
                disabled={profile && profile.tier === t.tier}
              >
                {profile && profile.tier === t.tier
                  ? "Current Plan"
                  : t.cta}
              </button>
            </div>
          ))}
        </div>
      </main>
    </>
  );
}
