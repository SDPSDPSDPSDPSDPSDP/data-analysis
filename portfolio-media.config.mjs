// Media the Portfolio site shows. From web/: `npm run portfolio:stills`, then `npm run portfolio:upload`.
// Lives at the repo root so portfolio-stills/ lands there. See the portfolio-media README.
// --local shoots the running `npm run dev` server, to check a layout change before deploying.
const url = process.argv.includes("--local") ? "http://localhost:6817" : "https://shirins-data-analysis.vercel.app";

export default {
  files: {
    "portfolio-media/data-ink-ratio.webp": "data-analysis/data-ink-ratio.webp",
  },
  stills: [
    // Past the home gallery's staggered fly-in.
    { slug: "data-analysis", id: "data-analysis-hero", url: `${url}/portfolio/home-static`, at: 3 },
  ],
};
