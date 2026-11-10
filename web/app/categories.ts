import type { Category, DataFormat, Example, PlotSectionData } from "@/lib/sections";
// Relative with extension: scripts/build-previews.mjs imports this file with plain Node, which knows no "@/" alias.
import { exampleSetup, withDarkMode } from "../lib/exampleSetup.ts";
import { parseExamples, previewPath } from "./exampleFiles.ts";

// Sections without a data format are tools: they draw no chart to prerender.
function section(title: string, file: string, ...dataFormats: DataFormat[]): PlotSectionData {
  const { setup, examples, homeExamples } = parseExamples(file);
  if (dataFormats.length === 0) return { title, dataFormats, setup, examples, homeExamples };
  const globalSetup = getGlobalSetup();
  const withPreview = (example: Example) => {
    const code = `${exampleSetup(globalSetup, setup, example)}\n${example.code}`;
    return { ...example, preview: previewPath(code), darkPreview: previewPath(withDarkMode(code, true)) };
  };
  return { title, dataFormats, setup, examples: examples.map(withPreview), homeExamples: homeExamples.map(withPreview) };
}

export function getCategories(): Category[] {
  const barCharts = [
    section("Barplots", "bar.py", {
      description: "Without value: one row per observation. The plot counts the rows per category.",
      columns: [
        { name: "fruit", role: "x or y" },
        { name: "is_ripe", role: "hue" },
      ],
      rows: [
        ["Apple", "True"],
        ["Apple", "False"],
        ["Apple", "False"],
        ["Orange", "True"],
      ],
    }, {
      description: "With value: one row per category and hue, with the value already calculated. The plot sums the values per category.",
      columns: [
        { name: "fruit", role: "x or y" },
        { name: "is_ripe", role: "hue" },
        { name: "count", role: "value" },
      ],
      rows: [
        ["Apple", "False", "5"],
        ["Apple", "True", "40"],
        ["Banana", "False", "12"],
        ["Banana", "True", "4"],
      ],
    }),
    section("Histograms", "histogram.py", {
      description: "One row per observation with a numeric value. The plot counts the rows per bin.",
      columns: [
        { name: "fruit", role: "" },
        { name: "sweetness", role: "x" },
        { name: "is_ripe", role: "hue" },
      ],
      rows: [
        ["Apple", "15.2", "True"],
        ["Apple", "8.7", "False"],
        ["Apple", "13.9", "True"],
        ["Orange", "10.4", "False"],
      ],
    }),
  ];
  const pieCharts = [
    section("Pie charts", "piechart.py", {
      description: "One row per observation. The plot counts the rows per value and shows each count as a slice.",
      columns: [
        { name: "fruit", role: "col" },
        { name: "is_ripe", role: "" },
      ],
      rows: [
        ["Apple", "True"],
        ["Apple", "False"],
        ["Cherry", "True"],
        ["Orange", "True"],
      ],
    }),
  ];
  const lineCharts = [
    section("Time plots", "time.py", {
      description: "With y: one row per x value and hue, with the y value already calculated. The plot draws one line per hue.",
      columns: [
        { name: "year", role: "x" },
        { name: "n_harvested", role: "y" },
        { name: "is_ripe", role: "hue" },
      ],
      rows: [
        ["2000", "83", "True"],
        ["2000", "44", "False"],
        ["2001", "199", "True"],
        ["2001", "68", "False"],
      ],
    }, {
      description: "Without y: one row per observation with a date. group_by counts the rows per year, month or day.",
      columns: [
        { name: "date", role: "x" },
        { name: "is_ripe", role: "hue" },
      ],
      rows: [
        ["2018-01-01", "True"],
        ["2018-01-01", "False"],
        ["2018-01-02", "True"],
        ["2018-01-04", "False"],
      ],
    }),
    section("Line plots", "line.py", {
      description: "One row per point with two numeric values. The plot draws a line through them; labels marks single points.",
      columns: [
        { name: "threshold", role: "labels" },
        { name: "coverage", role: "x" },
        { name: "accuracy", role: "y" },
        { name: "marked", role: "labels" },
      ],
      rows: [
        ["0.5", "0.932", "0.891", "0.5"],
        ["0.51", "0.926", "0.892", ""],
        ["0.52", "0.920", "0.893", ""],
        ["0.8", "0.490", "0.951", "0.8"],
      ],
    }),
  ];
  const scatterCharts = [
    section("Scatter plots", "scatter.py", {
      description: "One row per observation with two numeric values. The plot draws one point per row.",
      columns: [
        { name: "fruit", role: "hue" },
        { name: "weight", role: "x" },
        { name: "sweetness", role: "y" },
        { name: "days_on_tree", role: "size" },
      ],
      rows: [
        ["Apple", "221.4", "14.1", "32"],
        ["Cherry", "187.9", "11.6", "18"],
        ["Orange", "236.0", "15.3", "47"],
        ["Fig", "170.2", "9.8", "25"],
      ],
    }),
  ];
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
