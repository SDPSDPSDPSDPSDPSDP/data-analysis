import type { Metadata } from "next";
import HomeGallery from "@/components/domain/HomeGallery";
import { getCategories, getHomeCharts } from "@/app/categories";
import { getPinnedCharts } from "../pinned";
import "../portfolio.css";

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

export default function PortfolioHome() {
  const charts = getHomeCharts();
  return (
    <div className="portfolio-home">
      <HomeGallery categories={getCategories()} charts={charts} pinned={getPinnedCharts(charts)} />
    </div>
  );
}
