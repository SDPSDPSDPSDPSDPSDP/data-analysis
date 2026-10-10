import CodeBlock from "@/components/ui/CodeBlock";
import RunnableCode from "@/components/domain/RunnableCode";

export default function Playground({ setup, examples }: { setup: string; examples: string[] }) {
  return (
    <main className="page">
      <h1>shirin</h1>
      <CodeBlock value={setup} />
      {examples.map((code, i) => (
        <RunnableCode key={i} initialCode={code} setup={setup} />
      ))}
    </main>
  );
}
