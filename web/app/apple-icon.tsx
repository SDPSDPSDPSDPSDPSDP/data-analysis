import { ImageResponse } from "next/og";

export const dynamic = "force-static";
export const size = { width: 180, height: 180 };
export const contentType = "image/png";

// Three bars in the example palette. Mirrors app/icon.svg; next/og renders plain inline styles, not CSS tokens.
const BRAND_BG = "#1e1e1e";
const BARS = [
  { color: "#e9d0ff", height: 0.45 },
  { color: "#c7ff0f", height: 0.8 },
  { color: "#ffb752", height: 0.6 },
];
const MARK_SIZE = 120;
const BAR_WIDTH = MARK_SIZE * 0.18;
const MARK_HEIGHT = MARK_SIZE * 0.7;

// Full square: iOS rounds the corners itself.
export default function AppleIcon() {
  return new ImageResponse(
    (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "100%", height: "100%", background: BRAND_BG }}>
        <div style={{ display: "flex", alignItems: "flex-end", gap: MARK_SIZE * 0.08, height: MARK_HEIGHT }}>
          {BARS.map((bar) => (
            <div
              key={bar.color}
              style={{ width: BAR_WIDTH, height: MARK_HEIGHT * bar.height, background: bar.color, borderRadius: BAR_WIDTH / 2 }}
            />
          ))}
        </div>
      </div>
    ),
    size,
  );
}
