import type { Metadata } from "next";
import Link from "next/link";
import Nav from "@/components/domain/Nav";
import { getCategories } from "@/app/categories";

export const metadata: Metadata = {
  title: "Page not found",
  robots: { index: false },
  alternates: { canonical: null },
};

export default function NotFound() {
  return (
    <>
      <Nav categories={getCategories()} />
      <main className="page message-page">
        <h1>Page not found</h1>
        <p>This page does not exist, or it moved.</p>
        <Link href="/">Back to all charts</Link>
      </main>
    </>
  );
}
