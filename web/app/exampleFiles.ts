import { createHash } from "node:crypto";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import type { Example, SetupCell } from "@/components/domain/PlotSection";
import type { Skill } from "@/components/ui/SkillViewer";
// Relative with extension: scripts/build-previews.mjs imports this file with plain Node, which knows no "@/" alias.
import { withDarkMode } from "../lib/exampleSetup.ts";

// "# %% [setup] explanation" cells show their explanation and run before every example below them.
// "# %% [terminal] explanation" cells show their explanation and a Claude Code transcript; they never run.
// A "[chart]" line in a transcript shows the chart drawn by its code lines (indented four spaces).
// "# %% [skill] explanation" cells hold a skill folder path (relative to web/) and show that skill's files; they never run.
// "# %% [hidden]" cells run before every example below them but are not shown.
// Other "# %% label" cells are runnable examples; their labels are not shown.
// The home gallery shows every example except the first (already on the category page).
// A label ending in "[no-home]" keeps the example off the home gallery, "[home-only]" off the category page.
export function parseExamples(file: string) {
  const source = readFileSync(join(process.cwd(), "examples", file), "utf8");
  const cells = source
    .split(/^# %%[ \t]*/m)
    .filter((cell) => cell.trim())
    .map((cell) => {
      const [label, ...code] = cell.split("\n");
      return { label: label.trim(), code: code.join("\n").trim() };
    });
  const setup = cells.flatMap((cell): SetupCell[] => {
    const kind = /^\[(setup|terminal|skill)\]/.exec(cell.label)?.[1];
    if (!kind) return [];
    const explanation = cell.label.replace(`[${kind}]`, "").trim();
    if (kind === "skill") return [{ kind, explanation, code: cell.code, skill: readSkill(cell.code) }];
    if (kind === "terminal") return [{ kind, explanation, code: cell.code, chart: terminalChart(cell.code) }];
    return [{ kind: "code", explanation, code: cell.code }];
  });
  const hidden: string[] = [];
  const examples: Example[] = [];
  const homeExamples: Example[] = [];
  for (const cell of cells) {
    if (cell.label.startsWith("[hidden]")) hidden.push(cell.code);
    else if (!cell.label.startsWith("[")) {
      const example = { code: cell.code, hiddenSetup: hidden.join("\n\n"), preview: null, darkPreview: null };
      const homeOnly = cell.label.endsWith("[home-only]");
      if (!homeOnly) examples.push(example);
      if (homeOnly || (examples.length > 1 && !cell.label.endsWith("[no-home]"))) homeExamples.push(example);
    }
  }
  return { setup, examples, homeExamples };
}

function terminalChart(transcript: string) {
  const lines = transcript.split(/\r?\n/);
  if (!lines.includes("[chart]")) return null;
  const code = lines.filter((line) => line.startsWith("    ")).map((line) => line.slice(4));
  if (code.length === 0) throw new Error(`Transcript has a [chart] line but no code lines:\n${transcript}`);
  const chart = code.join("\n");
  return { light: previewPath(withDarkMode(chart, false)), dark: previewPath(withDarkMode(chart, true)) };
}

const FRONTMATTER = /^---\r?\n([\s\S]*?)\r?\n---\r?\n/;

// SKILL.md first, as Claude reads it; its frontmatter is shown as the header, not as file content.
// Folder layout is fixed by the plugin format: <plugin>/skills/<skill>/, manifest in <plugin>/.claude-plugin/.
function readSkill(folder: string): Skill {
  const dir = join(process.cwd(), folder);
  const skillSource = readFileSync(join(dir, "SKILL.md"), "utf8");
  const frontmatter = FRONTMATTER.exec(skillSource);
  if (!frontmatter) throw new Error(`${folder}/SKILL.md has no frontmatter`);
  const field = (key: string) => {
    const value = new RegExp(`^${key}:\\s*(.+)$`, "m").exec(frontmatter[1])?.[1];
    if (!value) throw new Error(`${folder}/SKILL.md frontmatter has no ${key}`);
    return value.trim();
  };
  const plugin = JSON.parse(readFileSync(join(dir, "..", "..", ".claude-plugin", "plugin.json"), "utf8"));
  const others = readdirSync(dir).filter((name) => name.endsWith(".md") && name !== "SKILL.md").sort();
  return {
    name: field("name"),
    description: field("description"),
    plugin: plugin.name,
    version: plugin.version,
    files: [
      { name: "SKILL.md", content: withoutTitle(skillSource.slice(frontmatter[0].length)) },
      ...others.map((name) => ({ name, content: withoutTitle(readFileSync(join(dir, name), "utf8")) })),
    ],
  };
}

// The file list already names each file, so its leading "# title" is not repeated.
function withoutTitle(markdown: string) {
  return markdown.trim().replace(/^# .*\r?\n/, "").trim();
}

// Code of every prerendered SVG by its path, filled as sections are built; read by scripts/build-previews.mjs.
export const previewCodes = new Map<string, string>();

export function previewPath(code: string) {
  const path = `/previews/${createHash("sha1").update(code).digest("hex").slice(0, 16)}.svg`;
  previewCodes.set(path, code);
  return path;
}
