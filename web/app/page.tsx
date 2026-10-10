import { readFileSync } from "node:fs";
import { join } from "node:path";
import Playground from "@/components/domain/Playground";

// "# %% label" cells: first is setup, the rest are runnable examples.
export default function Home() {
  const source = readFileSync(join(process.cwd(), "examples", "countplot.py"), "utf8");
  const [setup, ...examples] = source
    .split(/^# %%[ \t]*/m)
    .filter((cell) => cell.trim())
    .map((cell) => cell.replace(/^(.+)\n/, "# $1\n").trim());
  return <Playground setup={setup} examples={examples} />;
}
