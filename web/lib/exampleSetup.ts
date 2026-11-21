import type { Example, SetupCell } from "@/lib/sections";

export function exampleSetup(globalSetup: string, setup: SetupCell[], example: Example): string {
  const sectionCode = setup.filter((cell) => cell.kind === "code").map((cell) => cell.code);
  return [globalSetup, ...sectionCode, example.hiddenSetup].join("\n\n");
}

const CALL = "PlotGraphs(";
const DARK_MODE_ARG = /\s*\bdark_mode=(True|False)\s*,?/g;

// Index just past the `)` closing the call whose arguments start at `open`.
function callEnd(code: string, open: number): number {
  let depth = 1;
  let end = open;
  for (; end < code.length && depth > 0; end++) {
    const char = code[end];
    // Parens inside strings and comments, e.g. title="(n)", must not end the call.
    if (char === '"' || char === "'") end = closingQuote(code, end);
    else if (char === "#") end = lineEnd(code, end);
    else if (char === "(") depth++;
    else if (char === ")") depth--;
  }
  if (depth > 0) throw new Error(`Unclosed PlotGraphs( call:\n${code}`);
  return end;
}

function closingQuote(code: string, start: number): number {
  let end = start + 1;
  for (; end < code.length && code[end] !== code[start]; end++) if (code[end] === "\\") end++;
  return end;
}

function lineEnd(code: string, start: number): number {
  const end = code.indexOf("\n", start);
  return end < 0 ? code.length : end;
}

// Rewrites the arguments of every PlotGraphs(...) call; matches nested parens, e.g. palette=dict(...).
function mapPlotGraphsArgs(code: string, map: (args: string) => string): string {
  let out = "";
  let from = 0;
  for (let start = code.indexOf(CALL); start >= 0; start = code.indexOf(CALL, from)) {
    const open = start + CALL.length;
    const end = callEnd(code, open);
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
  if (!dark) return stripped;
  return mapPlotGraphsArgs(stripped, (args) => (args ? `${args}, dark_mode=True` : "dark_mode=True"));
}
