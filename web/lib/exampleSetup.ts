import type { Example, SetupCell } from "@/components/domain/PlotSection";

// Full code run before an example: global setup, section setup, then the example's hidden setup.
export function exampleSetup(globalSetup: string, setup: SetupCell[], example: Example): string {
  return [globalSetup, ...setup.map((cell) => cell.code), example.hiddenSetup].join("\n\n");
}
