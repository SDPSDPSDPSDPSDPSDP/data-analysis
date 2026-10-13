import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, unlinkSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// Repo root, so the count covers both the shirin package and the web site.
const ROOT = path.join(__dirname, "..", "..", "..");
const OUTPUT_FILE = path.join(ROOT, "web", "public", "portfolio", "LOC.txt");

// Generated output, example content and one-off scripts are not project source.
const EXCLUDE_DIRS = [
  "node_modules",
  ".git",
  ".next",
  "out",
  ".venv",
  ".vercel",
  ".claude",
  ".github",
  "scripts",
  "docs",
  "public",
  "assets",
  "examples",
  "shirin-charts",
  "archive",
  "plot_output",
  "data",
  "todo",
];

const INCLUDE_EXT = "py,ts,tsx,mts,css,js,jsx,mjs";
const REPORT_FILE_NAME = ".cloc-report.json";
const REPORT_FILE = path.join(ROOT, REPORT_FILE_NAME);

const args = [
  "--yes",
  "cloc",
  ".",
  `--exclude-dir=${EXCLUDE_DIRS.join(",")}`,
  `--include-ext=${INCLUDE_EXT}`,
  `--report-file=${REPORT_FILE_NAME}`,
  "--json",
];

const npxCmd = process.platform === "win32" ? "npx.cmd" : "npx";
const env = { ...process.env };
const pathKey = Object.keys(env).find((k) => k.toUpperCase() === "PATH") ?? "PATH";
const currentPath = env[pathKey] ?? "";
// cloc needs perl, which on Windows ships with Git.
if (process.platform === "win32" && !currentPath.includes("Git\\usr\\bin")) {
  env[pathKey] = currentPath ? `${currentPath};C:\\Program Files\\Git\\usr\\bin` : "C:\\Program Files\\Git\\usr\\bin";
}

execFileSync(npxCmd, args, { encoding: "utf8", cwd: ROOT, shell: true, env });
const report = JSON.parse(readFileSync(REPORT_FILE, "utf8"));
unlinkSync(REPORT_FILE);

const total = report.SUM.code;
mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
writeFileSync(OUTPUT_FILE, `${total}\n`);
console.log(`ok   LOC.txt  ->  ${total} lines of code`);
