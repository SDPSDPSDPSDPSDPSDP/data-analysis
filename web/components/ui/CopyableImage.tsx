"use client";

import { useEffect, useState } from "react";
import CopyButton from "@/components/ui/CopyButton";

// Clipboards only reliably accept PNG, so vector images are rasterized at this scale.
const RASTER_SCALE = 3;

async function toPng(src: string): Promise<Blob> {
  const image = new Image();
  image.src = src;
  await image.decode();
  const canvas = document.createElement("canvas");
  canvas.width = image.naturalWidth * RASTER_SCALE;
  canvas.height = image.naturalHeight * RASTER_SCALE;
  const context = canvas.getContext("2d");
  if (!context) throw new Error("Canvas 2D context unavailable");
  context.drawImage(image, 0, 0, canvas.width, canvas.height);
  return new Promise<Blob>((resolve, reject) =>
    canvas.toBlob((blob) => (blob ? resolve(blob) : reject(new Error("PNG encoding failed"))), "image/png"),
  );
}

export default function CopyableImage({ src, alt }: { src: string; alt: string }) {
  const [png, setPng] = useState<{ blob: Blob; url: string } | null>(null);

  useEffect(() => {
    let url: string | null = null;
    let cancelled = false;
    toPng(src).then((blob) => {
      if (cancelled) return;
      url = URL.createObjectURL(blob);
      setPng({ blob, url });
    });
    return () => {
      cancelled = true;
      if (url) URL.revokeObjectURL(url);
    };
  }, [src]);

  if (!png) return <div className="skeleton" role="status" aria-label="Rendering chart" />;

  return (
    <figure className="chart copyable">
      <img src={png.url} alt={alt} />
      <CopyButton copy={() => navigator.clipboard.write([new ClipboardItem({ "image/png": png.blob })])} />
    </figure>
  );
}
