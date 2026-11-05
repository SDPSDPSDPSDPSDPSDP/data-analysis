import { ImageResponse } from "next/og";
import { BRAND_BG, BRAND_TEXT, BRAND_TEXT_SECONDARY, BrandMark } from "@/app/brand";
import { SITE_DESCRIPTION, SITE_NAME } from "@/lib/site";

export const dynamic = "force-static";
export const alt = SITE_NAME;
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpenGraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 72,
          width: "100%",
          height: "100%",
          padding: 96,
          background: BRAND_BG,
        }}
      >
        <BrandMark size={300} />
        <div style={{ display: "flex", flexDirection: "column", gap: 24, flex: 1 }}>
          <div style={{ fontSize: 88, color: BRAND_TEXT }}>shirin</div>
          <div style={{ fontSize: 36, lineHeight: 1.3, color: BRAND_TEXT_SECONDARY }}>{SITE_DESCRIPTION}</div>
        </div>
      </div>
    ),
    size,
  );
}
