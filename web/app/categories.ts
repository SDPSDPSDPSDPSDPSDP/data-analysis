import type { Category } from "@/components/domain/Playground";
import type { DataFormat, Example, PlotSectionData } from "@/components/domain/PlotSection";
// Relative with extension: scripts/build-previews.mjs imports this file with plain Node, which knows no "@/" alias.
import { exampleSetup, withDarkMode } from "../lib/exampleSetup.ts";
import { parseExamples, previewCodes, previewPath } from "./exampleFiles.ts";

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
    section("Line charts", "time.py", {
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

function getGlobalSetup() {
  return getSetup()
    .map((cell) => cell.code)
    .join("\n\n");
}

const TITLE_LINE = /^[ \t]*title=(.*),[ \t]*\r?\n/m;

// Home gallery shows the title as text above the chart, so the preview is drawn without it.
function splitTitle(code: string) {
  const match = code.match(TITLE_LINE);
  if (!match) throw new Error(`Home gallery example has no single-line title=:\n${code}`);
  const [title, subtitle = null] = [...match[1].matchAll(/'([^']*)'|"([^"]*)"/g)].map((m) => m[1] ?? m[2]);
  if (title === undefined) throw new Error(`Home gallery title is not a string or list of strings: ${match[1]}`);
  return { title, subtitle, previewCode: code.replace(TITLE_LINE, "") };
}

// Home gallery charts. Sections without a data format are tools, not charts.
// cardPreview is the gallery image without title, preview the full chart for the modal. dark* are the dark_mode=True versions.
export function getHomeCharts() {
  const globalSetup = getGlobalSetup();
  return getCategories().flatMap((category) =>
    category.sections
      .filter((section) => section.dataFormats.length > 0)
      .flatMap((section) =>
        section.homeExamples.map((example) => {
          const setup = exampleSetup(globalSetup, section.setup, example);
          const { title, subtitle, previewCode } = splitTitle(example.code);
          const cardCode = `${setup}\n${previewCode}`;
          if (!example.preview || !example.darkPreview) throw new Error(`Home gallery example has no preview:\n${example.code}`);
          return {
            setup,
            code: example.code,
            title,
            subtitle,
            preview: example.preview,
            darkPreview: example.darkPreview,
            cardPreview: previewPath(cardCode),
            darkCardPreview: previewPath(withDarkMode(cardCode, true)),
            section: section.title,
            category: category.title,
          };
        }),
      ),
  );
}

// Every prerendered SVG with the code that draws it.
export function getPreviews() {
  getHomeCharts();
  return [...previewCodes].map(([path, code]) => ({ path, code }));
}
