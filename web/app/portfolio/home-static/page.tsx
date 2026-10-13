import type { Metadata } from "next";
import HomeGallery from "@/components/domain/HomeGallery";
import { getCategories, getHomeCharts } from "@/app/categories";
import "../portfolio.css";

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

/** Gallery still only; the iframe frames /portfolio/home with its nav. */
export default function PortfolioHomeStatic() {
  return (
    <div className="portfolio-still">
      <HomeGallery categories={getCategories()} charts={getHomeCharts()} showNav={false} />
    </div>
  );
}
