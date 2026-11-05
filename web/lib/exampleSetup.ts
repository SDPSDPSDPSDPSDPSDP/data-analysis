import type { Example, SetupCell } from "@/lib/sections";

export function exampleSetup(globalSetup: string, setup: SetupCell[], example: Example): string {
  const sectionCode = setup.filter((cell) => cell.kind === "code").map((cell) => cell.code);
  return [globalSetup, ...sectionCode, example.hiddenSetup].join("\n\n");
}

const CALL = "PlotGraphs(";
const DARK_MODE_ARG = /\s*\bdark_mode=(True|False)\s*,?/g;

// Palette grey too dark to read on the dark background, swapped for white in dark mode.
const LIGHT_GREY = '"#d6dde6"';
const WHITE = '"#ffffff"';

// Rewrites the arguments of every PlotGraphs(...) call; matches nested parens, e.g. palette=dict(...).
function mapPlotGraphsArgs(code: string, map: (args: string) => string): string {
  let out = "";
  let from = 0;
  for (let start = code.indexOf(CALL); start >= 0; start = code.indexOf(CALL, from)) {
    const open = start + CALL.length;
    let depth = 1;
    let end = open;
    for (; end < code.length && depth > 0; end++) {
      if (code[end] === "(") depth++;
      else if (code[end] === ")") depth--;
    }
    if (depth > 0) throw new Error(`Unclosed PlotGraphs( call:\n${code}`);
    out += code.slice(from, open) + map(code.slice(open, end - 1)) + ")";
    from = end;
  }
  return out + code.slice(from);
}

function withoutDarkMode(args: string): string {
  return args.replace(DARK_MODE_ARG, "").trim().replace(/,$/, "");
}

// Adds or removes dark_mode=True on every PlotGraphs(...) call, so the setup shows what draws the charts.
export function withDarkMode(code: string, dark: boolean): string {
  if (!code.includes(CALL)) throw new Error(`No PlotGraphs(...) call to toggle dark mode on:\n${code}`);
  const stripped = mapPlotGraphsArgs(code, withoutDarkMode);
  if (!dark) return stripped.replaceAll(WHITE, LIGHT_GREY);
  return mapPlotGraphsArgs(stripped.replaceAll(LIGHT_GREY, WHITE), (args) => (args ? `${args}, dark_mode=True` : "dark_mode=True"));
}
