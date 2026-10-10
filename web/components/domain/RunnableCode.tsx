"use client";

import { useEffect, useState } from "react";
import { hoverTooltip, keymap, Prec } from "@uiw/react-codemirror";
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
      dom.innerHTML = inlineMarkdown(doc);
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

  async function execute(source: string) {
    setResult(await run(`${setup}\n${source}`));
  }

  const runKey = Prec.highest(
    keymap.of([
      {
        key: "Mod-Enter",
        run: (view) => (execute(view.state.doc.toString()), true),
      },
    ]),
  );

  return (
    <div className="runnable">
      <CodeBlock value={code} onChange={setCode} extensions={[runKey, docTooltip]} />
      <section className="output">
        {result?.images.map((src, i) => (
          <CopyableImage key={i} src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(src)}`} alt="Rendered chart" />
        ))}
        {result?.stdout && <pre>{result.stdout}</pre>}
        {result?.error && <pre className="error">{result.error}</pre>}
        {!result && <p className="hint">Rendering chart…</p>}
      </section>
    </div>
  );
}
