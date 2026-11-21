// Sample tables for the bar and pie sections: the input shape its examples expect.
import type { DataFormat } from "@/lib/sections";

export const BAR_COUNTED: DataFormat = {
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
};

export const BAR_VALUES: DataFormat = {
  description:
    "With value: one row per category and hue, with the value already calculated. The plot sums the values per category.",
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
};

export const HISTOGRAM: DataFormat = {
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
};

export const PIE: DataFormat = {
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
};
