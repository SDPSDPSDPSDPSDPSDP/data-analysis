import { readFileSync } from "node:fs";
import { join } from "node:path";
import Playground from "@/components/domain/Playground";

export default function Home() {
  const code = readFileSync(join(process.cwd(), "examples", "countplot.py"), "utf8");
  return <Playground initialCode={code} />;
}
