import { readFileSync } from "node:fs";
import { join } from "node:path";
import Playground from "@/components/domain/Playground";

// "# %% [setup] explanation" cells run before every example and show their explanation.
// Other "# %% label" cells are runnable examples; their labels are not shown.
export default function Home() {
  const source = readFileSync(join(process.cwd(), "examples", "countplot.py"), "utf8");
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
  const examples = cells.filter((cell) => !cell.label.startsWith("[setup]")).map((cell) => cell.code);
  return <Playground title="Countplots" setup={setup} examples={examples} />;
}
