"use client";

import { useEffect, useRef, useState } from "react";
import { load, run, type RunResult } from "@/lib/pyodide";
import { DOC_TOOLTIP } from "@/lib/docTooltip";
import CodeBlock from "@/components/ui/CodeBlock";
import CopyableImage from "@/components/ui/CopyableImage";
import { useVisible } from "@/lib/useVisible";
import { useDarkMode } from "@/lib/darkMode";
import { useHydrated } from "@/lib/useHydrated";

type Props = {
  // Names the chart images for screen readers.
  title: string;
  initialCode: string;
  // Prepended to every run, not shown in the editor.
  setup: string;
  // Prerendered SVGs shown while Python loads, null shows a skeleton.
  preview: { light: string; dark: string } | null;
};

// The prerendered HTML cannot know the theme (set by an inline script), so it holds both previews and CSS shows one.
function previewImages(preview: Props["preview"], hydrated: boolean, dark: boolean) {
  if (!preview) return [];
  if (hydrated) return [{ src: dark ? preview.dark : preview.light }];
  return [
    { src: preview.light, theme: "light" as const },
    { src: preview.dark, theme: "dark" as const },
  ];
}

export default function RunnableCode({ title, initialCode, setup, preview }: Props) {
  const [code, setCode] = useState(initialCode);
  const [result, setResult] = useState<RunResult | null>(null);
  const root = useRef<HTMLDivElement>(null);
  const visible = useVisible(root);
  const dark = useDarkMode();
  const hydrated = useHydrated();

  // Python loads right away; the example only runs once visible.
  useEffect(() => {
    load().catch((err: Error) => setResult({ images: [], stdout: "", error: err.message }));
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
    ? result.images.map((src) => ({ src: `data:image/svg+xml;charset=utf-8,${encodeURIComponent(src)}` }))
    : previewImages(preview, hydrated, dark);

  return (
    <div className="runnable" ref={root}>
      <CodeBlock value={code} dark={dark} onChange={setCode} onRun={execute} extensions={DOC_TOOLTIP} />
      <section className="output">
        {/* Preview and result share one list so the first figure stays the same element when the result lands,
            keeping any animation running on it (the home modal flies it in). */}
        {images.map((image, i) => (
          <CopyableImage key={i} {...image} alt={`${title} chart`} />
        ))}
        {result?.stdout && <pre>{result.stdout}</pre>}
        {result?.error && <pre className="error">{result.error}</pre>}
        {!result && !preview && <div className="skeleton" role="status" aria-label="Rendering chart" />}
      </section>
    </div>
  );
}
