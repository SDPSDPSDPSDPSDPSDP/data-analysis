import type { HomeChart as Chart } from "@/lib/sections";

// Fixed chart per slot, row by row, as [category, title]: titles repeat across categories.
// null slots and the rest are shuffled.
type Slots = ([string, string] | null)[];

export const STILL_PINNED: Slots = [
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
  ["Bar charts", "Sour fruit"],
  ["Bar charts", "Fruit stock by ripeness"],
  ["Pie charts", "Fruit basket"],
  ["Scatter plots", "Heavier fruit is sweeter"],
];

// Live gallery leads its last row with the pie and scatter; the still keeps them at the end.
const LAST_ROW_START = 10;
const PIE_AND_SCATTER_START = 12;
export const HOME_PINNED: Slots = [
  ...STILL_PINNED.slice(0, LAST_ROW_START),
  ...STILL_PINNED.slice(PIE_AND_SCATTER_START),
  ...STILL_PINNED.slice(LAST_ROW_START, PIE_AND_SCATTER_START),
];

export function getPinnedCharts(charts: Chart[], slots: Slots): (Chart | null)[] {
  return slots.map((slot) => {
    if (slot === null) return null;
    const [category, title] = slot;
    const chart = charts.find((c) => c.category === category && c.title === title);
    if (!chart) throw new Error(`Portfolio: no home chart "${title}" in ${category}`);
    return chart;
  });
}
