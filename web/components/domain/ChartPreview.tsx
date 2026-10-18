import { useEffect, useRef, type CSSProperties } from "react";

type Props = {
  // Prerendered SVG from scripts/build-previews.mjs, drawn without its title.
  src: string;
  title: string;
  subtitle: string | null;
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
export default function ChartPreview({ src, title, subtitle, index, shrunk, hidden, returning, onOpen }: Props) {
  const button = useRef<HTMLButtonElement>(null);
  const card = useRef<HTMLSpanElement>(null);

  // Hover grows the card into its cell plus half the grid gap, so whitespace stays to its neighbours.
  useEffect(() => {
    const cell = button.current!;
    const inner = card.current!;
    const fit = () => {
      const gap = parseFloat(getComputedStyle(cell.parentElement!).rowGap);
      const room = Math.min(
        (cell.offsetWidth + gap) / inner.offsetWidth,
        (cell.offsetHeight + gap) / inner.offsetHeight,
      );
      inner.style.setProperty("--home-chart-fit-scale", String(room));
    };
    const observer = new ResizeObserver(fit);
    observer.observe(cell);
    observer.observe(inner);
    return () => observer.disconnect();
  }, []);

  return (
    <button
      ref={button}
      type="button"
      className={`chart-preview${shrunk ? " shrunk" : ""}${hidden ? " hidden" : ""}${returning ? " returning" : ""}`}
      style={{ "--i": index } as CSSProperties}
      onClick={(event) => onOpen(event.currentTarget)}
    >
      <span ref={card} className="chart-preview-card">
        <span className="chart-preview-title">{title}</span>
        {subtitle && <span className="chart-preview-subtitle">{subtitle}</span>}
        <img src={src} alt={title} loading="lazy" />
      </span>
    </button>
  );
}
