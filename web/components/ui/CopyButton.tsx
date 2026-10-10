"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";

export default function CopyButton({ copy }: { copy: () => Promise<void> }) {
  const [copied, setCopied] = useState(false);

  async function onClick() {
    await copy();
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <button className="copy-button" onClick={onClick} aria-label={copied ? "Copied" : "Copy"}>
      {copied ? <Check size="1em" /> : <Copy size="1em" />}
    </button>
  );
}
