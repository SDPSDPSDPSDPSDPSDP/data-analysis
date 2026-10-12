import { readFileSync } from "node:fs";
import { join } from "node:path";
import Playground from "@/components/domain/Playground";
import type { DataFormat, Example, PlotSectionData } from "@/components/domain/PlotSection";

// "# %% [setup] explanation" cells show their explanation and run before every example below them.
// "# %% [hidden]" cells run before every example below them but are not shown.
// Other "# %% label" cells are runnable examples; their labels are not shown.
function parseExamples(file: string) {
  const source = readFileSync(join(process.cwd(), "examples", file), "utf8");
  const cells = source
    .split(/^# %%[ \t]*/m)
    .filter((cell) => cell.trim())
    .map((cell) => {
      const [label, ...code] = cell.split("\n");
      return { label: label.trim(), code: code.join("\n").trim() };
    });
  const setup = cells
    .filter((cell) => cell.label.startsWith("[setup]"))
    .map((cell) => ({ explanation: cell.label.replace("[setup]", "").trim(), code: cell.code }));
  const hidden: string[] = [];
  const examples: Example[] = [];
  for (const cell of cells) {
    if (cell.label.startsWith("[hidden]")) hidden.push(cell.code);
    else if (!cell.label.startsWith("[")) examples.push({ code: cell.code, hiddenSetup: hidden.join("\n\n") });
  }
  return { setup, examples };
}

function section(title: string, file: string, ...dataFormats: DataFormat[]): PlotSectionData {
  return { title, dataFormats, ...parseExamples(file) };
}

export default function Home() {
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
  ];
  return (
    <Playground
      setup={parseExamples("setup.py").setup}
      categories={[
        { title: "Bar charts", sections: barCharts },
        { title: "Pie charts", sections: pieCharts },
        { title: "Line charts", sections: lineCharts },
        { title: "Scatter plots", sections: scatterCharts },
        { title: "Tools", sections: tools },
      ]}
    />
  );
}
