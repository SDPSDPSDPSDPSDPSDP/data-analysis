import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "shirin charts",
  description: "Write Python on the left, see the shirin chart on the right.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
