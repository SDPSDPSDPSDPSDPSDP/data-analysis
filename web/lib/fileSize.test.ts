// File size limit for source files in every language, repo-wide. Twin of
// tests/test_file_size.py: same languages, limits and exemptions, so a repo
// with only one of Node or Python still checks every file. ESLint `max-lines` only sees JS/TS.
import { readdirSync, readFileSync } from "node:fs";
import { join, relative, resolve } from "node:path";
import { expect, test } from "vitest";

const ROOT = resolve(__dirname, "../..");
const WARN_LOC = 100;
const MAX_LOC = 150;
// CSS stays on `//` `/*`: `#id` and `--token` are code there.
const HASH = ["#"];
const C_STYLE = ["//", "/*", "*"];
const SQL = ["--", "/*", "*"];
const COMMENT_PREFIXES: Record<string, string[]> = {
  ...Object.fromEntries("py pyi sh bash ps1 r rb".split(" ").map((ext) => [ext, HASH])),
  ...Object.fromEntries(
    "ts tsx mts cts js jsx mjs cjs css scss go rs java kt cs swift c h cpp hpp php"
      .split(" ")
      .map((ext) => [ext, C_STYLE]),
  ),
  ...Object.fromEntries("sql ddl".split(" ").map((ext) => [ext, SQL])),
};
const SKIP_DIRS = new Set([
  ".git",
  ".venv",
  "node_modules",
  ".next",
  ".mypy_cache",
  ".ruff_cache",
  ".pytest_cache",
  "__pycache__",
  "tests",
  "test",
  // Build outputs: setuptools copy of shirin/, Next static export.
  "build",
  "out",
]);
// Gitignored outputs at the repo root only: nested `data/` dirs are source.
const ROOT_SKIP_DIRS = new Set(["data", "models", "plots"]);
const GENERATED = new Set(["database.types.ts", "next-env.d.ts", "schema.sql"]);
const TEST_FILE = /(^test_.*|.*_test|.*\.(test|spec))\.[^.]+$|^conftest\.py$/;

function countLoc(path: string, prefixes: string[]): number {
  return readFileSync(path, "utf-8")
    .split(/\r?\n/)
    .filter((line) => line.trim() && !prefixes.some((p) => line.trimStart().startsWith(p))).length;
}

function sourceFiles(dir: string): [string, string[]][] {
  const files: [string, string[]][] = [];
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = join(dir, entry.name);
    if (entry.isDirectory()) {
      const skip = SKIP_DIRS.has(entry.name) || (dir === ROOT && ROOT_SKIP_DIRS.has(entry.name));
      if (!skip) files.push(...sourceFiles(path));
      continue;
    }
    const prefixes = COMMENT_PREFIXES[entry.name.split(".").pop()!.toLowerCase()];
    if (prefixes && !GENERATED.has(entry.name) && !TEST_FILE.test(entry.name)) {
      files.push([path, prefixes]);
    }
  }
  return files;
}

test("source files within size limit", () => {
  const tooLong: string[] = [];
  for (const [path, prefixes] of sourceFiles(ROOT)) {
    const loc = countLoc(path, prefixes);
    const name = relative(ROOT, path).replaceAll("\\", "/");
    if (loc > MAX_LOC) tooLong.push(`${name}: ${loc} LOC`);
    else if (loc > WARN_LOC) console.warn(`${name}: ${loc} LOC > ${WARN_LOC}. Consider splitting.`);
  }
  expect(tooLong, `Files over ${MAX_LOC} LOC, split them`).toEqual([]);
});
