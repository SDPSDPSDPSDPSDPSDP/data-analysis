"use client";

import { useEffect, useRef, useState } from "react";
import { hoverTooltip } from "@uiw/react-codemirror";
import { load, run, type RunResult } from "@/lib/pyodide";
import docstrings from "@/lib/docstrings.json";
import CodeBlock from "@/components/ui/CodeBlock";
import CopyableImage from "@/components/ui/CopyableImage";

const DOTTED_NAME = /^[A-Za-z_]\w*(\.[A-Za-z_]\w*)*$/;

// Inline markdown only: docstrings are Google-style, so a block parser would turn indented Args into code blocks.
function inlineMarkdown(text: string): string {
  const codes: string[] = [];
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/`([^`\n]+)`/g, (_, c) => `\u0000${codes.push(c) - 1}\u0000`)
    .replace(/\*\*(\S(?:[\s\S]*?\S)?)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|\W)([*_])(\S(?:[\s\S]*?\S)?)\2(?=\W|$)/g, "$1<em>$3</em>")
    .replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${codes[Number(i)]}</code>`);
}

// Unindented "Input:" lines are section headings; "    name:" lines start an argument.
// Docstring wraps (8-space continuation lines) are joined so Options/Default/Optional each get a line of their own.
function formatDoc(doc: string): string {
  return inlineMarkdown(doc.replace(/\n {8}(?=\S)/g, " "))
    .replace(/^([A-Z]\w*):$/gm, '<span class="doc-heading">$1</span>')
    .replace(/^ {4}(\w+):/gm, "<strong>$1</strong>:")
    .replace(/ (<em>(?:Optional|Default:.*?)<\/em>\.?)/g, '\n    <span class="doc-meta">$1</span>')
    .replace(/ (<strong>Options:<\/strong>.*)$/gm, '\n    <span class="doc-meta">$1</span>');
}

const DOCS: Record<string, string> = docstrings;

// Docstring of the dotted name under the cursor, looked up by its last part.
const docTooltip = hoverTooltip((view, pos) => {
  const line = view.state.doc.lineAt(pos);
  const offset = pos - line.from;
  const start = offset - line.text.slice(0, offset).match(/[\w.]*$/)![0].length;
  const end = offset + line.text.slice(offset).match(/^\w*/)![0].length;
  const name = line.text.slice(start, end);
  if (!DOTTED_NAME.test(name)) return null;
  const doc = DOCS[name.split(".").pop()!];
  if (!doc) return null;
  return {
    pos: line.from + start,
    end: line.from + end,
    create: () => {
      const dom = document.createElement("pre");
      dom.className = "doc-tooltip";
      dom.innerHTML = formatDoc(doc);
      return { dom };
    },
  };
});

type Props = {
  initialCode: string;
  // Prepended to every run, not shown in the editor.
  setup: string;
};

export default function RunnableCode({ initialCode, setup }: Props) {
  const [code, setCode] = useState(initialCode);
  const [result, setResult] = useState<RunResult | null>(null);

  useEffect(() => {
    load().then(
      () => execute(initialCode),
      (err) => setResult({ images: [], stdout: "", error: String(err) }),
    );
  }, []);

  // Running a setup cell (like after picking a palette color) re-renders the chart.
  const lastSetup = useRef(setup);
  useEffect(() => {
    if (lastSetup.current === setup) return;
    lastSetup.current = setup;
    execute(code);
  }, [setup]);

  async function execute(source: string) {
    setResult(await run(`${setup}\n${source}`));
  }

  return (
    <div className="runnable">
      <CodeBlock value={code} onChange={setCode} onRun={execute} extensions={[docTooltip]} />
      <section className="output">
        {result?.images.map((src, i) => (
          <CopyableImage key={i} src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(src)}`} alt="Rendered chart" />
        ))}
        {result?.stdout && <pre>{result.stdout}</pre>}
        {result?.error && <pre className="error">{result.error}</pre>}
        {!result && <div className="skeleton" role="status" aria-label="Rendering chart" />}
      </section>
    </div>
  );
}
