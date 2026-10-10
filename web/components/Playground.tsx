"use client";

import { useEffect, useState } from "react";
import CodeMirror, { keymap, Prec } from "@uiw/react-codemirror";
import { python } from "@codemirror/lang-python";
import { load, run, type RunResult } from "@/lib/pyodide";

type Status = "loading" | "ready" | "running" | "failed";

export default function Playground({ initialCode }: { initialCode: string }) {
  const [code, setCode] = useState(initialCode);
  const [status, setStatus] = useState<Status>("loading");
  const [result, setResult] = useState<RunResult | null>(null);

  useEffect(() => {
    load().then(
      () => setStatus("ready"),
      (err) => {
        setStatus("failed");
        setResult({ images: [], stdout: "", error: String(err) });
      },
    );
  }, []);

  async function execute(source: string) {
    setStatus("running");
    setResult(await run(source));
    setStatus("ready");
  }

  const runKey = Prec.highest(
    keymap.of([{ key: "Mod-Enter", run: (view) => (execute(view.state.doc.toString()), true) }]),
  );

  return (
    <main className="playground">
      <section className="pane">
        <div className="toolbar">
          <button onClick={() => execute(code)} disabled={status !== "ready"}>
            {status === "loading" ? "Loading Python…" : status === "running" ? "Running…" : "Run"}
          </button>
          <span className="hint">Ctrl+Enter</span>
        </div>
        <CodeMirror value={code} onChange={setCode} extensions={[python(), runKey]} height="100%" className="editor" />
      </section>
      <section className="pane output">
        {result?.images.map((src, i) => <Chart key={i} base64={src} />)}
        {result?.stdout && <pre>{result.stdout}</pre>}
        {result?.error && <pre className="error">{result.error}</pre>}
        {!result && <p className="hint">Press Run to render the chart.</p>}
      </section>
    </main>
  );
}

function Chart({ base64 }: { base64: string }) {
  const src = `data:image/png;base64,${base64}`;
  const [copied, setCopied] = useState(false);

  async function copy() {
    const blob = await fetch(src).then((r) => r.blob());
    await navigator.clipboard.write([new ClipboardItem({ "image/png": blob })]);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <figure className="chart">
      <img src={src} alt="Rendered chart" />
      <button onClick={copy}>{copied ? "Copied" : "Copy"}</button>
    </figure>
  );
}
