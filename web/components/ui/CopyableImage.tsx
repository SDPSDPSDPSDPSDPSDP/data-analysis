"use client";

import CopyButton from "@/components/ui/CopyButton";

export default function CopyableImage({ src, alt }: { src: string; alt: string }) {
  async function copy() {
    const blob = await fetch(src).then((r) => r.blob());
    await navigator.clipboard.write([new ClipboardItem({ [blob.type]: blob })]);
  }

  return (
    <figure className="chart copyable">
      <img src={src} alt={alt} />
      <CopyButton copy={copy} />
    </figure>
  );
}
