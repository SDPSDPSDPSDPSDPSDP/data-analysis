// Brand mark for the generated apple icon and Open Graph image: three bars in the example palette.
// Mirrors app/icon.svg; next/og renders plain inline styles, not CSS tokens.
export const BRAND_BG = "#1e1e1e";
export const BRAND_TEXT = "rgba(255, 255, 255, 0.93)";
export const BRAND_TEXT_SECONDARY = "rgba(255, 255, 255, 0.6)";
const BARS = [
  { color: "#e9d0ff", height: 0.45 },
  { color: "#c7ff0f", height: 0.8 },
  { color: "#ffb752", height: 0.6 },
];

export function BrandMark({ size }: { size: number }) {
  const barWidth = size * 0.18;
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: size * 0.08, height: size * 0.7 }}>
      {BARS.map((bar) => (
        <div
          key={bar.color}
          style={{ width: barWidth, height: size * 0.7 * bar.height, background: bar.color, borderRadius: barWidth / 2 }}
        />
      ))}
    </div>
  );
}
