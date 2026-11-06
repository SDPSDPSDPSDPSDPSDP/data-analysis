import type { Metadata } from "next";
import localFont from "next/font/local";
import OverlayScrollbar from "@/components/ui/OverlayScrollbar";
import { STORAGE_KEY } from "@/lib/darkModeKey";
import { SITE_DESCRIPTION, SITE_NAME, SITE_URL } from "@/lib/site";
import "./globals.css";
import "./base.css";
import "./message-page.css";
import "./nav.css";
import "./code.css";
import "./copy-button.css";
import "./doc-tooltip.css";
import "./terminal.css";
import "./skill.css";
import "./examples.css";
import "./data-table.css";
import "./more-examples.css";
import "./home.css";
import "./chart-modal-motion.css";
import "./chart-modal.css";

const futura = localFont({
  src: "../public/fonts/FuturaND-Medium.woff2",
  variable: "--font-futura",
});

const satoshi = localFont({
  src: [
    { path: "../public/fonts/Satoshi-Variable.woff2", weight: "300 900", style: "normal" },
    { path: "../public/fonts/Satoshi-VariableItalic.woff2", weight: "300 900", style: "italic" },
  ],
  variable: "--font-satoshi",
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: SITE_NAME, template: `%s - ${SITE_NAME}` },
  description: SITE_DESCRIPTION,
  alternates: { canonical: "./" },
  openGraph: { url: "./", siteName: SITE_NAME, type: "website", locale: "en" },
  twitter: { card: "summary_large_image" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    // The inline script sets data-theme before hydration, React would otherwise flag the mismatch.
    <html lang="en" className={`${futura.variable} ${satoshi.variable}`} suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            // Blocked storage (Safari private mode, sandboxed iframes) throws; dark stays the default then.
            __html: `let saved = null; try { saved = localStorage.getItem("${STORAGE_KEY}"); } catch {} if (saved !== "0") document.documentElement.dataset.theme = "dark"; document.documentElement.dataset.js = "";`,
          }}
        />
      </head>
      <body>
        {children}
        <OverlayScrollbar />
      </body>
    </html>
  );
}
