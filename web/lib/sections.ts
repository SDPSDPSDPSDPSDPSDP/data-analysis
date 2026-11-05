import type { Skill } from "@/components/ui/SkillViewer";

// "code" cells run before every example; "terminal" (Claude Code transcript) and "skill" cells are only shown.
export type SetupCell =
  | { kind: "code"; explanation: string; code: string }
  // chart: prerendered SVGs of the transcript's code, shown at its "[chart]" line.
  | { kind: "terminal"; explanation: string; code: string; chart: { light: string; dark: string } | null }
  | { kind: "skill"; explanation: string; code: string; skill: Skill };

export type DataFormat = {
  description: string;
  columns: { name: string; role: string }[];
  rows: string[][];
};

export type Example = {
  code: string;
  // Runs after the section setup, not shown.
  hiddenSetup: string;
  // Prerendered SVG shown until Python has run, null for examples that draw no chart.
  preview: string | null;
  darkPreview: string | null;
};

export type PlotSectionData = {
  title: string;
  dataFormats: DataFormat[];
  // Shown in the section and run before each of its examples, after the global setup.
  setup: SetupCell[];
  examples: Example[];
  homeExamples: Example[];
};

export function sectionId(title: string): string {
  return title.toLowerCase().replace(/\s+/g, "-");
}
