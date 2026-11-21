// Sample tables for the x/y chart sections (time, line, scatter): the input shape their examples expect.
import type { DataFormat } from "@/lib/sections";

export const TIME_VALUES: DataFormat = {
  description:
    "With y: one row per x value and hue, with the y value already calculated. The plot draws one line per hue.",
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
};

export const TIME_DATES: DataFormat = {
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
};

export const LINE: DataFormat = {
  description:
    "One row per point with two numeric values. The plot draws a line through them, one per hue; marks puts a dot on rows where it is True.",
  columns: [
    { name: "detector", role: "hue" },
    { name: "coverage", role: "x" },
    { name: "accuracy", role: "y" },
    { name: "marked", role: "marks" },
  ],
  rows: [
    ["Old detector", "0.932", "0.548", "True"],
    ["Old detector", "0.490", "0.590", "True"],
    ["New detector", "0.932", "0.666", "True"],
    ["New detector", "0.490", "0.762", "True"],
  ],
};

export const SCATTER: DataFormat = {
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
};
