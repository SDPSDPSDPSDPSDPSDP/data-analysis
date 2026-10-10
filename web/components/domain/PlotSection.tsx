import { ChevronDown } from "lucide-react";
import CodeBlock from "@/components/ui/CodeBlock";
import RunnableCode from "@/components/domain/RunnableCode";

export type SetupCell = {
  explanation: string;
  code: string;
};

export type DataFormat = {
  description: string;
  columns: { name: string; role: string }[];
  rows: string[][];
};

export type PlotSectionData = {
  title: string;
  dataFormat: DataFormat;
  // Shown in the section and run before each of its examples, after the global setup.
  setup: SetupCell[];
  hiddenSetup: string;
  examples: string[];
};

export function sectionId(title: string): string {
  return title.toLowerCase().replace(/\s+/g, "-");
}

type Props = PlotSectionData & {
  globalSetup: string;
  expandAll: boolean;
};

export default function PlotSection({ title, dataFormat, setup, hiddenSetup, examples, globalSetup, expandAll }: Props) {
  const setupCode = [globalSetup, ...setup.map((cell) => cell.code), hiddenSetup].join("\n\n");
  const moreExamples = examples
    .slice(1)
    .map((code, i) => <RunnableCode key={i} initialCode={code} setup={setupCode} />);
  return (
    <>
      <h3 id={sectionId(title)}>{title}</h3>
      {setup.map((cell, i) => (
        <section key={i} className="setup-cell">
          <p>{cell.explanation}</p>
          <CodeBlock value={cell.code} />
        </section>
      ))}
      <section className="data-format">
        <div className="setup-cell">
          <h4>Data format</h4>
          <p>{dataFormat.description}</p>
          <table className="data-table">
            <thead>
              <tr>
                {dataFormat.columns.map((col) => (
                  <th key={col.name}>
                    {col.name} <span className="data-table-role">{col.role}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {dataFormat.rows.map((row, i) => (
                <tr key={i}>
                  {row.map((cell, j) => (
                    <td key={j}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="setup-cell">
          <h4>Example</h4>
          <RunnableCode initialCode={examples[0]} setup={setupCode} />
        </div>
      </section>
      {expandAll ? (
        moreExamples
      ) : (
        <details className="more-examples">
          <summary>
            <span className="more-examples-button">
              {examples.length - 1} more examples
              <ChevronDown size="1em" aria-hidden />
            </span>
          </summary>
          {moreExamples}
        </details>
      )}
    </>
  );
}
