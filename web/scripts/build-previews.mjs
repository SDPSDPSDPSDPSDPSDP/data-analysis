// Prerenders every example chart to public/previews/, so pages show them without waiting
// for Pyodide. Python replaces them in the browser once it has run the example.
import { execFileSync } from "node:child_process";
import { mkdirSync, readdirSync, rmSync } from "node:fs";
import { getPreviews } from "../app/categories.ts";

// Names are content hashes: clear old ones so edited examples leave no stale files.
// Empties the folder instead of removing it: on Windows a file watcher holding it open makes rmdir fail with EBUSY.
mkdirSync("public/previews", { recursive: true });
for (const file of readdirSync("public/previews")) rmSync(`public/previews/${file}`, { recursive: true, force: true });
const charts = getPreviews().map((chart) => ({ path: `public${chart.path}`, code: chart.code }));
execFileSync("uv", ["run", "python", "scripts/render_previews.py"], { input: JSON.stringify(charts), stdio: ["pipe", "inherit", "inherit"] });
console.log(`rendered ${charts.length} previews to public/previews`);
