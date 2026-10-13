import type { Example, SetupCell } from "@/components/domain/PlotSection";

// Full code run before an example: global setup, section setup, then the example's hidden setup.
export function exampleSetup(globalSetup: string, setup: SetupCell[], example: Example): string {
  return [globalSetup, ...setup.map((cell) => cell.code), example.hiddenSetup].join("\n\n");
}

const PLOT_GRAPHS = /PlotGraphs\(([^)]*)\)/g;
const DARK_MODE_ARG = /,\s*dark_mode=(True|False)/g;

// Palette colors too dark to read on the dark background, swapped for a lighter one in dark mode.
const DARK_PALETTE_SWAPS: [light: string, dark: string][] = [
  ['"#d6dde6"', '"#ffffff"'],
];

// Adds or removes dark_mode=True on every PlotGraphs(...) call, so the setup shows what draws the charts.
export function withDarkMode(code: string, dark: boolean): string {
  if (!code.includes("PlotGraphs(")) throw new Error(`No PlotGraphs(...) call to toggle dark mode on:\n${code}`);
  const stripped = code.replace(PLOT_GRAPHS, (call) => call.replace(DARK_MODE_ARG, ""));
  const swapped = DARK_PALETTE_SWAPS.reduce(
    (acc, [light, darkColor]) => (dark ? acc.replaceAll(light, darkColor) : acc.replaceAll(darkColor, light)),
    stripped,
  );
  return dark ? swapped.replace(PLOT_GRAPHS, "PlotGraphs($1, dark_mode=True)") : swapped;
}
