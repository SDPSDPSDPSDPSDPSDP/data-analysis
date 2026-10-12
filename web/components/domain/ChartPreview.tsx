"use client";

import { useRef, type CSSProperties } from "react";

type Props = {
  // Prerendered SVG from scripts/build-previews.mjs, drawn without its title.
  src: string;
  title: string;
  subtitle: string | null;
  // Position in the grid, staggers the entrance animation.
  index: number;
  // Gets the card so the modal can animate out of it.
  onOpen: (card: HTMLElement) => void;
};

// Chart only, no code: opens the example in a modal where it can be edited.
export default function ChartPreview({ src, title, subtitle, index, onOpen }: Props) {
  const card = useRef<HTMLSpanElement>(null);
  return (
    <button
      type="button"
      className="chart-preview"
      style={{ "--i": index } as CSSProperties}
      onClick={() => onOpen(card.current!)}
    >
      <span className="chart-preview-card" ref={card}>
        <span className="chart-preview-title">{title}</span>
        {subtitle && <span className="chart-preview-subtitle">{subtitle}</span>}
        <img src={src} alt={title} loading="lazy" />
      </span>
    </button>
  );
}
