import { readFileSync } from "node:fs";
import { join } from "node:path";
import { ImageResponse } from "next/og";

export const dynamic = "force-static";
export const size = { width: 180, height: 180 };
export const contentType = "image/png";

// Rasterizes app/icon.svg so the favicon stays the single source of the mark's colors.
const ICON_SRC = `data:image/svg+xml;base64,${readFileSync(join(process.cwd(), "app/icon.svg")).toString("base64")}`;

// Full square: iOS rounds the corners itself, so fill behind icon.svg's rounded corners.
export default function AppleIcon() {
  return new ImageResponse(
    <div style={{ display: "flex", width: "100%", height: "100%", background: "white" }}>
      <img src={ICON_SRC} width={size.width} height={size.height} alt="" />
    </div>,
    size,
  );
}
