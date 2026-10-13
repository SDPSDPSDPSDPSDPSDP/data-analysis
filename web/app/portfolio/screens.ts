export type PortfolioScreen = {
  title: string;
  path: string;
};

export const PORTFOLIO_SCREENS: readonly PortfolioScreen[] = [
  {
    title: "Home",
    path: "/portfolio/home",
  },
  {
    title: "Home (still)",
    path: "/portfolio/home-static",
  },
];
