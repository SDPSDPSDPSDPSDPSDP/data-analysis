"use client";

import { useEffect, useState } from "react";
import { keymap, Prec } from "@uiw/react-codemirror";
import { load, run, type RunResult } from "@/lib/pyodide";
import CodeBlock from "@/components/ui/CodeBlock";
import CopyableImage from "@/components/ui/CopyableImage";

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
      <CodeBlock value={code} onChange={setCode} extensions={[runKey]} />
      <section className="output">
        {result?.images.map((src, i) => (
          <CopyableImage key={i} src={`data:image/png;base64,${src}`} alt="Rendered chart" />
        ))}
        {result?.stdout && <pre>{result.stdout}</pre>}
        {result?.error && <pre className="error">{result.error}</pre>}
        {!result && <p className="hint">Rendering chart…</p>}
      </section>
    </div>
  );
}
