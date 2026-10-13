import type { Metadata } from "next";
import HomeGallery from "@/components/domain/HomeGallery";
import { getCategories, getHomeCharts } from "@/app/categories";
import "../portfolio.css";

export const metadata: Metadata = {
  robots: { index: false, follow: false },
};

// Fixed chart per slot, row by row, as [category, title]: titles repeat across categories.
// null slots and the rest are shuffled.
const PINNED: ([string, string] | null)[] = [
  ["Scatter plots", "Days on tree"],
  ["Bar charts", "Sweetness, ripe vs unripe"],
  ["Bar charts", "Fruits A to Z"],
  ["Bar charts", "Share of all fruit"],
  ["Pie charts", "Ripe vs unripe fruit"],
  ["Bar charts", "Which fruit sells best"],
  ["Line charts", "Fruits picked per month"],
  ["Bar charts", "Share of fruit sold"],
  ["Bar charts", "Ripe vs unripe fruit"],
  ["Bar charts", "Fruit sweetness"],
  ["Bar charts", "Sour fruit"],
  ["Bar charts", "Fruit stock by ripeness"],
  ["Pie charts", "Fruit basket"],
  ["Scatter plots", "Heavier fruit is sweeter"],
];

// Three full rows of --portfolio-still-columns.
const LIMIT = 15;

/** Gallery still only; the iframe frames /portfolio/home with its nav. */
export default function PortfolioHomeStatic() {
  const charts = getHomeCharts();
  const pinned = PINNED.map((slot) => {
    if (slot === null) return null;
    const [category, title] = slot;
    const chart = charts.find((c) => c.category === category && c.title === title);
    if (!chart) throw new Error(`Portfolio still: no home chart "${title}" in ${category}`);
    return chart;
  });
  return (
    <div className="portfolio-still">
      <HomeGallery categories={getCategories()} charts={charts} showNav={false} pinned={pinned} limit={LIMIT} />
    </div>
  );
}
