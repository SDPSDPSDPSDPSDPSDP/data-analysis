// Prerenders the home gallery charts to public/previews/, so the gallery shows them
// without waiting for Pyodide. Python only runs in the browser once a chart is opened.
import { execFileSync } from "node:child_process";
import { mkdirSync, rmSync } from "node:fs";
import { getHomeCharts } from "../app/categories.ts";

// Names are content hashes: clear old ones so edited examples leave no stale files.
rmSync("public/previews", { recursive: true, force: true });
mkdirSync("public/previews");
const charts = getHomeCharts().map((chart) => ({ path: `public${chart.preview}`, code: `${chart.setup}\n${chart.code}` }));
execFileSync("uv", ["run", "python", "scripts/render_previews.py"], { input: JSON.stringify(charts), stdio: ["pipe", "inherit", "inherit"] });
console.log(`rendered ${charts.length} previews to public/previews`);
