"use client";

import Link from "next/link";

// Shows a render error instead of a blank page; the error is still thrown and logged, not hidden.
export default function ErrorPage({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <main className="page message-page">
      <h1>Something went wrong</h1>
      <pre className="error">{error.message}</pre>
      <p>
        <button type="button" className="message-page-button" onClick={reset}>
          Try again
        </button>{" "}
        or <Link href="/">go back to all charts</Link>.
      </p>
    </main>
  );
}
