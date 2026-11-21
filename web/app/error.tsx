"use client";

import Link from "next/link";
import LinkButton from "@/components/ui/LinkButton";
import ErrorText from "@/components/ui/ErrorText";

// Shows a render error instead of a blank page; the error is still thrown and logged, not hidden.
export default function ErrorPage({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <main className="page message-page">
      <h1>Something went wrong</h1>
      <ErrorText>{error.message}</ErrorText>
      <p>
        <LinkButton onClick={reset}>Try again</LinkButton> or <Link href="/">go back to all charts</Link>.
      </p>
    </main>
  );
}
