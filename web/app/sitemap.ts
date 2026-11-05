import type { MetadataRoute } from "next";
import { getCategories } from "@/app/categories";
import { sectionId } from "@/components/domain/PlotSection";
import { SITE_URL } from "@/lib/site";

export const dynamic = "force-static";

export default function sitemap(): MetadataRoute.Sitemap {
  const paths = ["", "/all", ...getCategories().map((category) => `/${sectionId(category.title)}`)];
  return paths.map((path) => ({ url: `${SITE_URL}${path}` }));
}
