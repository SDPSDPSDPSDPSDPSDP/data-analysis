import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { Example } from "@/components/domain/PlotSection";

// "# %% [setup] explanation" cells show their explanation and run before every example below them.
// "# %% [terminal] explanation" cells show their explanation and a Claude Code transcript; they never run.
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
  const setup = cells
    .filter((cell) => cell.label.startsWith("[setup]") || cell.label.startsWith("[terminal]"))
    .map((cell) => ({
      explanation: cell.label.replace(/^\[(setup|terminal)\]/, "").trim(),
      code: cell.code,
      terminal: cell.label.startsWith("[terminal]"),
    }));
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

// Code of every prerendered SVG by its path, filled as sections are built; read by scripts/build-previews.mjs.
export const previewCodes = new Map<string, string>();

export function previewPath(code: string) {
  const path = `/previews/${createHash("sha1").update(code).digest("hex").slice(0, 16)}.svg`;
  previewCodes.set(path, code);
  return path;
}
