import CodeBlock from "@/components/ui/CodeBlock";
import DataFormatTable from "@/components/ui/DataFormatTable";
import SkillViewer from "@/components/ui/SkillViewer";
import TerminalBlock from "@/components/ui/TerminalBlock";
import MoreExamples from "@/components/domain/MoreExamples";
import RunnableCode from "@/components/domain/RunnableCode";
import { exampleSetup } from "@/lib/exampleSetup";
import { useDarkMode } from "@/lib/darkMode";
import { sectionId, type Example, type PlotSectionData, type SetupCell } from "@/lib/sections";

function SetupCellBody({ cell, dark }: { cell: SetupCell; dark: boolean }) {
  if (cell.kind === "skill") return <SkillViewer skill={cell.skill} />;
  if (cell.kind === "terminal") {
    const chart = cell.chart && (dark ? cell.chart.dark : cell.chart.light);
    return <TerminalBlock transcript={cell.code} chart={chart} />;
  }
  return <CodeBlock value={cell.code} />;
}

type Props = PlotSectionData & {
  globalSetup: string;
  // Only section of its category: takes the category's heading level instead.
  standalone: boolean;
  expanded: boolean;
};

export default function PlotSection({ title, dataFormats, setup, examples, globalSetup, standalone, expanded }: Props) {
  const dark = useDarkMode();
  const runnable = (example: Example, key?: number) => (
    <RunnableCode
      key={key}
      title={title}
      initialCode={example.code}
      preview={dark ? example.darkPreview : example.preview}
      setup={exampleSetup(globalSetup, setup, example)}
    />
  );
  const moreExamples = examples.slice(1).map((example, i) => runnable(example, i));
  const Heading = standalone ? "h2" : "h3";
  const SubHeading = standalone ? "h3" : "h4";
  const heading = (
    <>
      <Heading id={sectionId(title)}>{title}</Heading>
      {setup.map((cell, i) => (
        <section key={i} className="setup-cell">
          {cell.explanation && <p>{cell.explanation}</p>}
          <SetupCellBody cell={cell} dark={dark} />
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
          <SubHeading>{dataFormats.length > 1 ? "Data formats" : "Data format"}</SubHeading>
          {dataFormats.map((dataFormat, k) => (
            <div key={k} className="setup-cell">
              <p>{dataFormat.description}</p>
              <DataFormatTable columns={dataFormat.columns} rows={dataFormat.rows} />
            </div>
          ))}
        </div>
        <div className="setup-cell">
          <SubHeading>Example</SubHeading>
          {runnable(examples[0])}
        </div>
      </section>
      <MoreExamples title={title} count={examples.length - 1} expanded={expanded}>
        {moreExamples}
      </MoreExamples>
    </>
  );
}
