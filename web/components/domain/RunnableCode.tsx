"use client";

import { useEffect, useRef, useState } from "react";
import { load, run, type RunResult } from "@/lib/pyodide";
import { DOC_TOOLTIP } from "@/lib/docTooltip";
import CodeBlock from "@/components/ui/CodeBlock";
import CopyableImage from "@/components/ui/CopyableImage";
import { useVisible } from "@/lib/useVisible";

type Props = {
  // Names the chart images for screen readers.
  title: string;
  initialCode: string;
  // Prepended to every run, not shown in the editor.
  setup: string;
  // Prerendered SVG shown while Python loads, null shows a skeleton.
  preview: string | null;
};

export default function RunnableCode({ title, initialCode, setup, preview }: Props) {
  const [code, setCode] = useState(initialCode);
  const [result, setResult] = useState<RunResult | null>(null);
  const root = useRef<HTMLDivElement>(null);
  const visible = useVisible(root);

  // Python loads right away; the example only runs once visible.
  useEffect(() => {
    load().catch((err) => setResult({ images: [], stdout: "", error: String(err) }));
  }, []);

  // Running a setup cell (like after picking a palette color) re-renders the chart.
  // An example that has not run yet picks up the new setup when it becomes visible.
  useEffect(() => {
    if (visible) execute(code);
  }, [visible, setup]);

  async function execute(source: string) {
    setResult(await run(`${setup}\n${source}`));
  }

  const images = result
    ? result.images.map((src) => `data:image/svg+xml;charset=utf-8,${encodeURIComponent(src)}`)
    : preview
      ? [preview]
      : [];

  return (
    <div className="runnable" ref={root}>
      <CodeBlock value={code} onChange={setCode} onRun={execute} extensions={DOC_TOOLTIP} />
      <section className="output">
        {/* Preview and result share one list so the first figure stays the same element when the result lands,
            keeping any animation running on it (the home modal flies it in). */}
        {images.map((src, i) => (
          <CopyableImage key={i} src={src} alt={`${title} chart`} />
        ))}
        {result?.stdout && <pre>{result.stdout}</pre>}
        {result?.error && <pre className="error">{result.error}</pre>}
        {!result && !preview && <div className="skeleton" role="status" aria-label="Rendering chart" />}
      </section>
    </div>
  );
}
