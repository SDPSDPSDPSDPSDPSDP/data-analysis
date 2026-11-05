import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/site";

export const dynamic = "force-static";

export default function robots(): MetadataRoute.Robots {
  // /portfolio is embed-only, see middleware.js.
  return { rules: { userAgent: "*", allow: "/", disallow: "/portfolio" }, sitemap: `${SITE_URL}/sitemap.xml` };
}
