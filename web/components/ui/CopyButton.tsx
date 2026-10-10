"use client";

import { useState } from "react";

export default function CopyButton({ copy }: { copy: () => Promise<void> }) {
  const [copied, setCopied] = useState(false);

  async function onClick() {
    await copy();
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <button className="copy-button" onClick={onClick}>
      {copied ? "Copied" : "Copy"}
    </button>
  );
}
