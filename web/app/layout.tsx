import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";

const futura = localFont({
  src: "../public/fonts/FuturaND-Medium.woff2",
  variable: "--font-futura",
});

export const metadata: Metadata = {
  title: "shirin charts",
  description: "Write Python on the left, see the shirin chart on the right.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={futura.variable}>
      <body>{children}</body>
    </html>
  );
}
