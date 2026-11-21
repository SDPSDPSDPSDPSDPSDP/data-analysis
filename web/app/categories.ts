import type { Category, DataFormat, Example, PlotSectionData } from "@/lib/sections";
// Relative with extension: scripts/build-previews.mjs imports this file with plain Node, which knows no "@/" alias.
import { exampleSetup, withDarkMode } from "../lib/exampleSetup.ts";
import { BAR_COUNTED, BAR_VALUES, HISTOGRAM, PIE } from "./dataFormats.ts";
import { LINE, SCATTER, TIME_DATES, TIME_VALUES } from "./xyDataFormats.ts";
import { parseExamples, previewPath } from "./exampleFiles.ts";

// Sections without a data format are tools: they draw no chart to prerender.
// Takes the global setup so it is read and parsed once per getCategories call, not once per section.
const sectionBuilder =
  (globalSetup: string) =>
  (title: string, file: string, ...dataFormats: DataFormat[]): PlotSectionData => {
    const { setup, examples, homeExamples } = parseExamples(file);
    if (dataFormats.length === 0) return { title, dataFormats, setup, examples, homeExamples };
    const withPreview = (example: Example) => {
      const code = `${exampleSetup(globalSetup, setup, example)}\n${example.code}`;
      return { ...example, preview: previewPath(code), darkPreview: previewPath(withDarkMode(code, true)) };
    };
    return {
      title,
      dataFormats,
      setup,
      examples: examples.map(withPreview),
      homeExamples: homeExamples.map(withPreview),
    };
  };

export function getCategories(): Category[] {
  const section = sectionBuilder(getGlobalSetup());
  const barCharts = [
    section("Barplots", "bar.py", BAR_COUNTED, BAR_VALUES),
    section("Histograms", "histogram.py", HISTOGRAM),
  ];
  const pieCharts = [section("Pie charts", "piechart.py", PIE)];
  const lineCharts = [
    section("Time plots", "time.py", TIME_VALUES, TIME_DATES),
    section("Line plots", "line.py", LINE),
  ];
  const scatterCharts = [section("Scatter plots", "scatter.py", SCATTER)];
  const tools = [
    section("Number formatting", "number_format.py"),
    section("Statistics", "stats.py"),
    section("DB2 connection", "sql.py"),
    section("Claude plugin", "claude_plugin.py"),
  ];
  return [
    { title: "Bar charts", sections: barCharts },
    { title: "Pie charts", sections: pieCharts },
    { title: "Line charts", sections: lineCharts },
    { title: "Scatter plots", sections: scatterCharts },
    { title: "Tools", sections: tools },
  ];
}

export function getSetup() {
  return parseExamples("setup.py").setup;
}

export function getGlobalSetup() {
  return getSetup()
    .map((cell) => cell.code)
    .join("\n\n");
}
