import { ImageResponse } from "next/og";
import { BRAND_BG, BrandMark } from "@/app/brand";

export const dynamic = "force-static";
export const size = { width: 180, height: 180 };
export const contentType = "image/png";

// Full square: iOS rounds the corners itself.
export default function AppleIcon() {
  return new ImageResponse(
    (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", width: "100%", height: "100%", background: BRAND_BG }}>
        <BrandMark size={120} />
      </div>
    ),
    size,
  );
}
