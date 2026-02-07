"""Feature detection from idea text.

Scans the idea description for keywords and returns a set of feature flags
that drive stack selection, prompt generation, and documentation.
"""

from typing import Dict, Set

FEATURE_KEYWORDS: Dict[str, list] = {
    "realtime": [
        "realtime", "real-time", "chat", "live", "stream", "websocket",
        "live update", "collaborative", "multiplayer", "presence",
        "instant messaging", "socket",
    ],
    "payments": [
        "marketplace", "payments", "billing", "subscription", "checkout",
        "stripe", "pricing", "plan", "tier", "invoice", "e-commerce",
        "shopping cart", "order", "purchase", "monetization", "paywall",
    ],
    "ai": [
        "recommend", " ai ", "machine learning", " ml ", "llm", "assistant",
        "agent", "gpt", "claude", "embeddings", "vector", "rag", "chatbot",
        "generation", "prediction", "classification", "nlp", "sentiment",
        "ai-powered", "intelligent", "smart suggest",
    ],
    "mobile": [
        "mobile", "ios", "android", "push notification", "responsive",
        "pwa", "react native", "flutter", "native app", "app store",
    ],
    "analytics": [
        "analytics", "dashboard", "reporting", "metrics", "kpi",
        "visualization", "chart", "graph", "tracking", "insights",
        "data visualization",
    ],
    "file_upload": [
        "upload", "file", "image", "video", "media", "attachment",
        "storage", "s3", "cdn", "gallery", "document", "photo",
        "avatar", "asset",
    ],
    "notifications": [
        "notification", "email", "sms", "alert", "webhook",
        "in-app notification", "digest", "reminder", "push",
    ],
    "search": [
        "search", "filter", "facet", "elasticsearch", "full-text",
        "autocomplete", "typeahead", "fuzzy", "explore", "discover",
    ],
    "social": [
        "social", "profile", "follow", "feed", "comment", "like",
        "share", "community", "forum", "post", "thread", "reaction",
        "mention", "friend", "connection",
    ],
    "i18n": [
        "i18n", "internationalization", "localization", "multi-language",
        "translation", "locale", "rtl", "multilingual",
    ],
    "multi_tenancy": [
        "multi-tenant", "tenant", "organization", "workspace",
        "team", "saas", "white-label", "subdomain", "org",
    ],
    "scheduling": [
        "schedule", "calendar", "booking", "appointment", "cron",
        "recurring", "reminder", "event", "availability", "time slot",
    ],
    "admin_panel": [
        "admin", "backoffice", "cms", "content management",
        "moderation", "management panel", "back office", "internal tool",
    ],
    "auth_advanced": [
        "sso", "oauth", "2fa", "mfa", "rbac", "role", "permission",
        "access control", "saml", "ldap", "single sign-on",
    ],
    "geolocation": [
        "map", "location", "geo", "gps", "address", "routing",
        "nearby", "distance", "place", "coordinate",
    ],
}

FEATURE_DESCRIPTIONS: Dict[str, str] = {
    "realtime": (
        "Real-time communication using WebSockets with presence tracking, "
        "live updates, and event broadcasting"
    ),
    "payments": (
        "Payment processing with Stripe integration, subscription management, "
        "invoicing, and checkout flows"
    ),
    "ai": (
        "AI/ML integration with LLM orchestration, prompt engineering, "
        "embeddings, and intelligent features"
    ),
    "mobile": (
        "Mobile-optimized API design with push notifications, offline-first "
        "patterns, and responsive interfaces"
    ),
    "analytics": (
        "Analytics dashboards with data visualization, KPI tracking, "
        "reporting, and user behavior insights"
    ),
    "file_upload": (
        "File upload system with cloud storage, image processing, "
        "CDN delivery, and media management"
    ),
    "notifications": (
        "Multi-channel notification system with email, SMS, in-app alerts, "
        "and webhook integrations"
    ),
    "search": (
        "Full-text search with faceted filtering, autocomplete, "
        "relevance tuning, and indexing"
    ),
    "social": (
        "Social features including user profiles, feeds, comments, "
        "reactions, follows, and community interaction"
    ),
    "i18n": (
        "Internationalization with multi-language support, locale management, "
        "RTL layout, and translation workflows"
    ),
    "multi_tenancy": (
        "Multi-tenant architecture with organization/workspace isolation, "
        "tenant-scoped data, and SaaS billing"
    ),
    "scheduling": (
        "Scheduling system with calendar views, booking flows, availability "
        "management, and recurring events"
    ),
    "admin_panel": (
        "Admin panel with content management, moderation tools, "
        "user management, and internal dashboards"
    ),
    "auth_advanced": (
        "Advanced authentication with SSO, MFA/2FA, role-based access "
        "control (RBAC), and fine-grained permissions"
    ),
    "geolocation": (
        "Geolocation features with maps, address lookup, proximity search, "
        "routing, and location-based services"
    ),
}


def detect_features(text: str) -> Set[str]:
    """Scan *text* for keywords and return matching feature flags."""
    lower = f" {text.lower()} "
    flags: Set[str] = set()
    for flag, keywords in FEATURE_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            flags.add(flag)
    return flags


def describe_features(flags: Set[str]) -> str:
    """Return a bullet-list description for the detected features."""
    if not flags:
        return "No advanced features detected — standard CRUD application."
    lines = []
    for flag in sorted(flags):
        desc = FEATURE_DESCRIPTIONS.get(flag, flag)
        lines.append(f"- **{flag}**: {desc}")
    return "\n".join(lines)
