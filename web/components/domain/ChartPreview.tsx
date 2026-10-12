type Props = {
  // Prerendered SVG from scripts/build-previews.mjs.
  src: string;
  onOpen: () => void;
};

// Chart only, no code: opens the example in a modal where it can be edited.
export default function ChartPreview({ src, onOpen }: Props) {
  return (
    <button type="button" className="chart-preview" onClick={onOpen}>
      <img src={src} alt="Example chart" loading="lazy" />
    </button>
  );
}
