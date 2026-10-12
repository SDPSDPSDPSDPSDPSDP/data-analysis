"use client";

import { useEffect, useRef, useState } from "react";
import { run, type RunResult } from "@/lib/pyodide";
import { useVisible } from "@/lib/useVisible";

type Props = {
  setup: string;
  code: string;
  onOpen: () => void;
};

// Chart only, no code: opens the example in a modal where it can be edited.
export default function ChartPreview({ setup, code, onOpen }: Props) {
  const [result, setResult] = useState<RunResult | null>(null);
  const root = useRef<HTMLButtonElement>(null);
  const visible = useVisible(root);

  useEffect(() => {
    if (visible) run(`${setup}\n${code}`).then(setResult);
  }, [visible, setup, code]);

  return (
    <button type="button" className="chart-preview" ref={root} onClick={onOpen}>
      {result?.images.map((src, i) => (
        <img key={i} src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(src)}`} alt="Example chart" />
      ))}
      {result?.error && <pre className="error">{result.error}</pre>}
      {!result && <div className="skeleton" role="status" aria-label="Rendering chart" />}
    </button>
  );
}
