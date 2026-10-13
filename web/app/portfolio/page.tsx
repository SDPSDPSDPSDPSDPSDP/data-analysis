import Link from "next/link";
import type { Metadata } from "next";
import { PORTFOLIO_SCREENS } from "./screens";
import "./portfolio.css";

export const metadata: Metadata = {
  title: { absolute: "Portfolio" },
  robots: { index: false, follow: false },
};

/** Not embedded or linked; a helper for whoever builds the portfolio. */
export default function PortfolioIndexPage() {
  return (
    <main className="portfolio-index">
      <h1 className="portfolio-index-title">Portfolio</h1>
      <ul className="portfolio-index-list">
        {PORTFOLIO_SCREENS.map((screen) => (
          <li key={screen.path}>
            <Link href={screen.path} className="portfolio-index-link">
              {screen.title}
            </Link>
            <span className="portfolio-index-path">{screen.path}</span>
          </li>
        ))}
      </ul>
    </main>
  );
}
