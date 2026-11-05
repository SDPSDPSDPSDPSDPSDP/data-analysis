// Renders app/opengraph-image.png: the light home gallery cards in the portfolio still's order.
// Run `npm run og` after the previews change (npm run prebuild regenerates them).
import { execFileSync } from "node:child_process";
import { getHomeCharts } from "../app/homeCharts.ts";
import { STILL_PINNED, getPinnedCharts } from "../app/portfolio/pinned.ts";

const charts = getHomeCharts();
const pinned = getPinnedCharts(charts, STILL_PINNED);
const rest = charts.filter((chart) => !pinned.some((slot) => slot?.cardPreview === chart.cardPreview));
const ordered = [...pinned.filter(Boolean), ...rest];
const paths = ordered.map((chart) => `public${chart.cardPreview}`);
execFileSync("uv", ["run", "python", "scripts/render_og.py", "app/opengraph-image.png"], {
  input: JSON.stringify(paths),
  stdio: ["pipe", "inherit", "inherit"],
});
console.log(`rendered ${paths.length} charts to app/opengraph-image.png`);
