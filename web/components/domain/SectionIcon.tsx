import { ChartArea, ChartBarBig, ChartColumn, ChartLine, ChartPie, ChartScatter, Database, Hash, Sigma, Wrench, type LucideIcon } from "lucide-react";

// Keyed by category or section title: icon components can't be passed from the server page.
const SECTION_ICONS: Record<string, LucideIcon> = {
  "Bar charts": ChartColumn,
  Barplots: ChartBarBig,
  Histograms: ChartArea,
  "Pie charts": ChartPie,
  "Line charts": ChartLine,
  "Scatter plots": ChartScatter,
  Tools: Wrench,
  "Number formatting": Hash,
  Statistics: Sigma,
  "DB2 connection": Database,
};

export default function SectionIcon({ title }: { title: string }) {
  const Icon = SECTION_ICONS[title];
  if (!Icon) throw new Error(`No icon for section "${title}"`);
  return <Icon size="1em" aria-hidden />;
}
