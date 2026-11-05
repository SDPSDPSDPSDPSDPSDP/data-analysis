"use client";

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

// Rasterized only on copy; the promise keeps the clipboard write inside the click's user gesture (Safari).
type Props = {
  src: string;
  alt: string;
  // Shown only in this theme, for markup rendered before the theme is known.
  theme?: "light" | "dark";
};

export default function CopyableImage({ src, alt, theme }: Props) {
  return (
    <figure className={theme ? `chart copyable ${theme}-only` : "chart copyable"}>
      <img
        src={src}
        alt={alt}
        onLoad={(event) => {
          const image = event.currentTarget;
          image.style.setProperty("--aspect", String(image.naturalWidth / image.naturalHeight));
        }}
      />
      <CopyButton copy={() => navigator.clipboard.write([new ClipboardItem({ "image/png": toPng(src) })])} />
    </figure>
  );
}
