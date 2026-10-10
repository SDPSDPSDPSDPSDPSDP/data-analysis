import CodeBlock from "@/components/ui/CodeBlock";
import RunnableCode from "@/components/domain/RunnableCode";

type SetupCell = {
  explanation: string;
  code: string;
};

type Props = {
  title: string;
  setup: SetupCell[];
  examples: string[];
};

export default function Playground({ title, setup, examples }: Props) {
  const setupCode = setup.map((cell) => cell.code).join("\n\n");
  return (
    <main className="page">
      <h1>shirin</h1>
      {setup.map((cell, i) => (
        <section key={i} className="setup-cell">
          <p>{cell.explanation}</p>
          <CodeBlock value={cell.code} />
        </section>
      ))}
      <h2>{title}</h2>
      {examples.map((code, i) => (
        <RunnableCode key={i} initialCode={code} setup={setupCode} />
      ))}
    </main>
  );
}
