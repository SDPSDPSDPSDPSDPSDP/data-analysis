type Props = {
  // Prerendered SVG from scripts/build-previews.mjs, drawn without its title.
  src: string;
  title: string;
  subtitle: string | null;
  onOpen: () => void;
};

// Chart only, no code: opens the example in a modal where it can be edited.
export default function ChartPreview({ src, title, subtitle, onOpen }: Props) {
  return (
    <button type="button" className="chart-preview" onClick={onOpen}>
      <span className="chart-preview-card">
        <span className="chart-preview-title">{title}</span>
        {subtitle && <span className="chart-preview-subtitle">{subtitle}</span>}
        <img src={src} alt={title} loading="lazy" />
      </span>
    </button>
  );
}
