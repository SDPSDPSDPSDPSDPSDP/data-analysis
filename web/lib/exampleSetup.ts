import type { Example, SetupCell } from "@/components/domain/PlotSection";

// Full code run before an example: global setup, section setup, then the example's hidden setup.
export function exampleSetup(globalSetup: string, setup: SetupCell[], example: Example): string {
  return [globalSetup, ...setup.map((cell) => cell.code), example.hiddenSetup].join("\n\n");
}

const PLOT_GRAPHS = /PlotGraphs\(([^)]*)\)/g;
const DARK_MODE_ARG = /,\s*dark_mode=(True|False)/g;

// Palette grey too dark to read on the dark background, swapped for white in dark mode.
const LIGHT_GREY = '"#d6dde6"';
const WHITE = '"#ffffff"';

// Adds or removes dark_mode=True on every PlotGraphs(...) call, so the setup shows what draws the charts.
export function withDarkMode(code: string, dark: boolean): string {
  if (!code.includes("PlotGraphs(")) throw new Error(`No PlotGraphs(...) call to toggle dark mode on:\n${code}`);
  const stripped = code.replace(PLOT_GRAPHS, (call) => call.replace(DARK_MODE_ARG, ""));
  if (!dark) return stripped.replaceAll(WHITE, LIGHT_GREY);
  return stripped
    .replaceAll(LIGHT_GREY, WHITE)
    .replace(PLOT_GRAPHS, (_, args: string) => `PlotGraphs(${args ? `${args}, ` : ""}dark_mode=True)`);
}
