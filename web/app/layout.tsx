import type { Metadata } from "next";
import localFont from "next/font/local";
import OverlayScrollbar from "@/components/ui/OverlayScrollbar";
import { STORAGE_KEY } from "@/lib/darkModeKey";
import "./globals.css";
import "./base.css";
import "./nav.css";
import "./code.css";
import "./terminal.css";
import "./skill.css";
import "./examples.css";
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
  title: { default: "Shirin's Charts", template: "%s - Shirin's Charts" },
  description: "SVG charts for pandas DataFrames in one line of Python. Edit and run every example in the browser.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    // The inline script sets data-theme before hydration, React would otherwise flag the mismatch.
    <html lang="en" className={`${futura.variable} ${satoshi.variable}`} suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            // Blocked storage (Safari private mode, sandboxed iframes) throws; dark stays the default then.
            __html: `let saved = null; try { saved = localStorage.getItem("${STORAGE_KEY}"); } catch {} if (saved !== "0") document.documentElement.dataset.theme = "dark";`,
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
