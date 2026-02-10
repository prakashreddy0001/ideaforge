export default function robots() {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://ideaforge.dev";

  return {
    rules: [
      {
        userAgent: "*",
        allow: ["/", "/pricing"],
        disallow: [
          "/admin",
          "/admin/*",
          "/dashboard",
          "/generate",
          "/refine",
          "/design-to-code",
          "/login",
          "/register",
          "/auth/*",
        ],
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
