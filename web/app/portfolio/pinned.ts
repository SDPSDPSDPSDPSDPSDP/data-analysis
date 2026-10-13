import { getHomeCharts } from "@/app/categories";

type Chart = ReturnType<typeof getHomeCharts>[number];

// Fixed chart per slot, row by row, as [category, title]: titles repeat across categories.
// null slots and the rest are shuffled.
const PINNED: ([string, string] | null)[] = [
  ["Scatter plots", "Days on tree"],
  ["Bar charts", "Sweetness, ripe vs unripe"],
  ["Bar charts", "Fruits A to Z"],
  ["Bar charts", "Share of all fruit"],
  ["Pie charts", "Ripe vs unripe fruit"],
  ["Bar charts", "Which fruit sells best"],
  ["Line charts", "Fruits picked per month"],
  ["Bar charts", "Share of fruit sold"],
  ["Bar charts", "Ripe vs unripe fruit"],
  ["Bar charts", "Fruit sweetness"],
  ["Pie charts", "Fruit basket"],
  ["Scatter plots", "Heavier fruit is sweeter"],
  ["Bar charts", "Sour fruit"],
  ["Bar charts", "Fruit stock by ripeness"],
];

export function getPinnedCharts(charts: Chart[]): (Chart | null)[] {
  return PINNED.map((slot) => {
    if (slot === null) return null;
    const [category, title] = slot;
    const chart = charts.find((c) => c.category === category && c.title === title);
    if (!chart) throw new Error(`Portfolio: no home chart "${title}" in ${category}`);
    return chart;
  });
}
