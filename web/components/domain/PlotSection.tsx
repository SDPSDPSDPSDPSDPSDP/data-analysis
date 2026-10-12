import { ChevronDown } from "lucide-react";
import CodeBlock from "@/components/ui/CodeBlock";
import RunnableCode from "@/components/domain/RunnableCode";
import SectionIcon from "@/components/domain/SectionIcon";

export type SetupCell = {
  explanation: string;
  code: string;
};

export type DataFormat = {
  description: string;
  columns: { name: string; role: string }[];
  rows: string[][];
};

export type Example = {
  code: string;
  // Runs after the section setup, not shown.
  hiddenSetup: string;
};

export type PlotSectionData = {
  title: string;
  dataFormats: DataFormat[];
  // Shown in the section and run before each of its examples, after the global setup.
  setup: SetupCell[];
  examples: Example[];
};

export function sectionId(title: string): string {
  return title.toLowerCase().replace(/\s+/g, "-");
}

type Props = PlotSectionData & {
  globalSetup: string;
  // Only section of its category: takes the category's heading level instead.
  standalone: boolean;
  expanded: boolean;
};

export default function PlotSection({ title, dataFormats, setup, examples, globalSetup, standalone, expanded }: Props) {
  const runnable = (example: Example, key?: number) => (
    <RunnableCode
      key={key}
      initialCode={example.code}
      setup={[globalSetup, ...setup.map((cell) => cell.code), example.hiddenSetup].join("\n\n")}
    />
  );
  const moreExamples = examples.slice(1).map((example, i) => runnable(example, i));
  const Heading = standalone ? "h2" : "h3";
  const heading = (
    <>
      <Heading id={sectionId(title)}>{title}</Heading>
      {setup.map((cell, i) => (
        <section key={i} className="setup-cell">
          {cell.explanation && <p>{cell.explanation}</p>}
          <CodeBlock value={cell.code} />
        </section>
      ))}
    </>
  );
  // Tools: no data format, every example shown.
  if (dataFormats.length === 0) {
    return (
      <>
        {heading}
        <div className="tool-examples">{examples.map((example, i) => runnable(example, i))}</div>
      </>
    );
  }
  return (
    <>
      {heading}
      <section className="data-format">
        <div className="setup-cell">
          <h4>{dataFormats.length > 1 ? "Data formats" : "Data format"}</h4>
          {dataFormats.map((dataFormat, k) => (
            <div key={k} className="setup-cell">
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
          ))}
        </div>
        <div className="setup-cell">
          <h4>Example</h4>
          {runnable(examples[0])}
        </div>
      </section>
      <details className="more-examples" open={expanded}>
        <summary>
          <span className="more-examples-button">
            <SectionIcon title={title} />
            <span className="more-examples-closed">{examples.length - 1} more examples</span>
            <span className="more-examples-open">Hide examples</span>
            <ChevronDown size="1em" className="more-examples-chevron" aria-hidden />
          </span>
        </summary>
        {moreExamples}
      </details>
    </>
  );
}
