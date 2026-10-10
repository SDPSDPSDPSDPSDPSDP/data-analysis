"use client";

import { useEffect, useState } from "react";
import { keymap, Prec } from "@uiw/react-codemirror";
import { load, run, type RunResult } from "@/lib/pyodide";
import CodeBlock from "@/components/ui/CodeBlock";
import CopyableImage from "@/components/ui/CopyableImage";

// Shown above the editor and prepended to every run.
const SETUP = `from shirin.plot import PlotGraphs
from shirin.assets.fake_data import df

plot = PlotGraphs(font='satoshi')`;

type Status = "loading" | "ready" | "running" | "failed";

export default function Playground({ initialCode }: { initialCode: string }) {
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
    setResult(await run(`${SETUP}\n${source}`));
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
    <main>
      <header className="header">
        <h1>Shirin</h1>
        <CodeBlock value={SETUP} />
      </header>
      <div className="playground">
        <section className="pane">
          <div className="toolbar">
            <button onClick={() => execute(code)} disabled={status !== "ready"}>
              {status === "loading"
                ? "Loading Python…"
                : status === "running"
                  ? "Running…"
                  : "Run"}
            </button>
            <span className="hint">Ctrl+Enter</span>
          </div>
          <CodeBlock value={code} onChange={setCode} extensions={[runKey]} className="editor" />
        </section>
        <section className="pane output">
          {result?.images.map((src, i) => (
            <CopyableImage key={i} src={`data:image/png;base64,${src}`} alt="Rendered chart" />
          ))}
          {result?.stdout && <pre>{result.stdout}</pre>}
          {result?.error && <pre className="error">{result.error}</pre>}
          {!result && <p className="hint">Rendering chart…</p>}
        </section>
      </div>
    </main>
  );
}
