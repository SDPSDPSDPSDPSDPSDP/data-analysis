"use client";

import { useState } from "react";

export default function CopyableImage({ src, alt }: { src: string; alt: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    const blob = await fetch(src).then((r) => r.blob());
    await navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })]);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <figure className="chart">
      <img src={src} alt={alt} />
      <button onClick={copy}>{copied ? "Copied" : "Copy"}</button>
    </figure>
  );
}
