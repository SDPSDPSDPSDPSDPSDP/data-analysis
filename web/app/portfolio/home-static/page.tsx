import type { Metadata } from "next";
import HomeGallery from "@/components/domain/HomeGallery";
import { getCategories, getHomeCharts } from "@/app/categories";
import { getPinnedCharts } from "../pinned";
import "../portfolio.css";

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

// Three full rows of --portfolio-still-columns.
const LIMIT = 15;

/** Gallery still only; the iframe frames /portfolio/home with its nav. */
export default function PortfolioHomeStatic() {
  const charts = getHomeCharts();
  return (
    <div className="portfolio-still">
      <HomeGallery categories={getCategories()} charts={charts} showNav={false} pinned={getPinnedCharts(charts)} limit={LIMIT} />
    </div>
  );
}
