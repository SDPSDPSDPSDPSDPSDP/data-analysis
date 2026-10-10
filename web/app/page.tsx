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
        ["Mango", "True"],
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
        ["Mango", "10.4", "False"],
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
        ["Mango", "True"],
      ],
    }),
  ];
  return (
    <Playground
      setup={parseExamples("setup.py").setup}
      categories={[
        { title: "Bar charts", sections: barCharts },
        { title: "Pie charts", sections: pieCharts },
      ]}
    />
  );
}
