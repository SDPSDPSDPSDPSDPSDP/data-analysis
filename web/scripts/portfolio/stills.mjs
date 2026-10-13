#!/usr/bin/env node

// Gallery stills for the Portfolio site, one per frame id. Tune `at` (seconds) here, then rerun
// `npm run portfolio:stills`. How it works: Portfolio/scripts/capture-stills.mjs.
import { fileURLToPath, pathToFileURL } from "node:url";
import { captureStills } from "../../../../../Portfolio/scripts/capture-stills.mjs";

const url = process.env.SITE_BASE_URL ?? "https://shirins-data-analysis.vercel.app";

export const STILLS = [
  // Past the home gallery's staggered fly-in.
  { slug: "charts", id: "charts-hero", url: `${url}/portfolio/home-static`, at: 3 },
];

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  const { chromium } = await import("playwright");
  // capture-stills writes portfolio-stills/ under cwd; repo root, like the other projects.
  process.chdir(fileURLToPath(new URL("../../..", import.meta.url)));
  await captureStills(chromium, STILLS);
}
