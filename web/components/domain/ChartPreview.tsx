import type { CSSProperties } from "react";

type Props = {
  // Prerendered SVG from scripts/build-previews.mjs, drawn without its title.
  src: string;
  title: string;
  subtitle: string | null;
  dark: boolean;
  // Position in the grid, staggers the entrance animation.
  index: number;
  // Another card was clicked, this one shrinks out of the way.
  shrunk: boolean;
  // Its modal is open, the modal chart took its place.
  hidden: boolean;
  // Its modal chart is flying back, this one fades in as the chart fades out.
  returning: boolean;
  // Gets the card button, its transition timing decides when the modal opens.
  onOpen: (card: HTMLElement) => void;
};

// Chart only, no code: opens the example in a modal where it can be edited.
export default function ChartPreview({ src, title, subtitle, dark, index, shrunk, hidden, returning, onOpen }: Props) {
  return (
    <button
      type="button"
      className={`chart-preview${shrunk ? " shrunk" : ""}${hidden ? " hidden" : ""}${returning ? " returning" : ""}`}
      style={{ "--i": index } as CSSProperties}
      onClick={(event) => onOpen(event.currentTarget)}
    >
      <span className={`chart-preview-card${dark ? " dark" : ""}`}>
        <span className="chart-preview-title">{title}</span>
        {subtitle && <span className="chart-preview-subtitle">{subtitle}</span>}
        <img src={src} alt={title} loading="lazy" />
      </span>
    </button>
  );
}
