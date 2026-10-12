"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { run, type RunResult } from "@/lib/pyodide";
import { useVisible } from "@/lib/useVisible";

type Props = {
  code: string;
  href: string;
};

// Chart only, no code: links to the page where the example can be edited.
export default function ChartPreview({ code, href }: Props) {
  const [result, setResult] = useState<RunResult | null>(null);
  const root = useRef<HTMLAnchorElement>(null);
  const visible = useVisible(root);

  useEffect(() => {
    if (visible) run(code).then(setResult);
  }, [visible, code]);

  return (
    <Link href={href} className="chart-preview" ref={root}>
      {result?.images.map((src, i) => (
        <img key={i} src={`data:image/svg+xml;charset=utf-8,${encodeURIComponent(src)}`} alt="Example chart" />
      ))}
      {result?.error && <pre className="error">{result.error}</pre>}
      {!result && <div className="skeleton" role="status" aria-label="Rendering chart" />}
    </Link>
  );
}
