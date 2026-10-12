import type { Metadata } from "next";
import localFont from "next/font/local";
import OverlayScrollbar from "@/components/ui/OverlayScrollbar";
import "./globals.css";
import "./nav.css";
import "./code.css";
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
  title: "shirin charts",
  description: "Write Python on the left, see the shirin chart on the right.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${futura.variable} ${satoshi.variable}`}>
      <body>
        {children}
        <OverlayScrollbar />
      </body>
    </html>
  );
}
