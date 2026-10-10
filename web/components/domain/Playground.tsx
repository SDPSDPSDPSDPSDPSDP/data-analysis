import CodeBlock from "@/components/ui/CodeBlock";
import RunnableCode from "@/components/domain/RunnableCode";

const SETUP = `from shirin.plot import PlotGraphs
from shirin.assets.demo_data import df

plot = PlotGraphs(font='satoshi')`;

export default function Playground({ initialCode }: { initialCode: string }) {
  return (
    <main className="page">
      <h1>Shirin</h1>
      <CodeBlock value={SETUP} />
      <RunnableCode initialCode={initialCode} setup={SETUP} />
    </main>
  );
}
