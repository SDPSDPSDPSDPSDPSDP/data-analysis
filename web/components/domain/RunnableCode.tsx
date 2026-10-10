"use client";

import { useEffect, useState } from "react";
import { keymap, Prec } from "@uiw/react-codemirror";
import { Play } from "lucide-react";
import { load, run, type RunResult } from "@/lib/pyodide";
import CodeBlock from "@/components/ui/CodeBlock";
import CopyableImage from "@/components/ui/CopyableImage";

type Status = "loading" | "ready" | "running" | "failed";

type Props = {
  initialCode: string;
  // Prepended to every run, not shown in the editor.
  setup: string;
};

export default function RunnableCode({ initialCode, setup }: Props) {
  const [code, setCode] = useState(initialCode);
  const [status, setStatus] = useState<Status>("loading");
  const [result, setResult] = useState<RunResult | null>(null);

  useEffect(() => {
    load().then(
      () => execute(initialCode),
      (err) => {
        setStatus("failed");
        setResult({ images: [], stdout: "", error: String(err) });
      },
    );
  }, []);

  async function execute(source: string) {
    setStatus("running");
    setResult(await run(`${setup}\n${source}`));
    setStatus("ready");
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
      <CodeBlock value={code} onChange={setCode} extensions={[runKey]}>
        <button
          className="run-button"
          onClick={() => execute(code)}
          disabled={status !== "ready"}
          title="Ctrl+Enter"
        >
          <Play size="1em" />
          {status === "loading" ? "Loading Python…" : status === "running" ? "Running…" : "Run"}
        </button>
      </CodeBlock>
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
