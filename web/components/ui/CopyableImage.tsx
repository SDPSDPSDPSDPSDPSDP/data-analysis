"use client";

import CopyButton from "@/components/ui/CopyButton";

// Clipboards only reliably accept PNG, so vector images are rasterized at this scale.
const COPY_SCALE = 3;

export default function CopyableImage({ src, alt }: { src: string; alt: string }) {
  async function copy() {
    const image = new Image();
    image.src = src;
    await image.decode();
    const canvas = document.createElement("canvas");
    canvas.width = image.naturalWidth * COPY_SCALE;
    canvas.height = image.naturalHeight * COPY_SCALE;
    const context = canvas.getContext("2d");
    if (!context) throw new Error("Canvas 2D context unavailable");
    context.drawImage(image, 0, 0, canvas.width, canvas.height);
    const png = await new Promise<Blob>((resolve, reject) =>
      canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error("PNG encoding failed"))), "image/png"),
    );
    await navigator.clipboard.write([new ClipboardItem({ "image/png": png })]);
  }

  return (
    <figure className="chart copyable">
      <img src={src} alt={alt} />
      <CopyButton copy={copy} />
    </figure>
  );
}
