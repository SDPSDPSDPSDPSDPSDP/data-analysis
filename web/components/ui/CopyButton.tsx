"use client";

import { useState } from "react";
import { Check, Copy, X } from "lucide-react";

type State = "idle" | "copied" | "failed";

const LABELS: Record<State, string> = { idle: "Copy", copied: "Copied", failed: "Copy failed" };
const ICONS: Record<State, typeof Copy> = { idle: Copy, copied: Check, failed: X };

export default function CopyButton({ copy }: { copy: () => Promise<void> }) {
  const [state, setState] = useState<State>("idle");

  async function onClick() {
    try {
      await copy();
      setState("copied");
    } catch (err) {
      // Clipboard denied or unsupported (no ClipboardItem): show it, and still surface the error.
      setState("failed");
      throw err;
    } finally {
      setTimeout(() => setState("idle"), 1500);
    }
  }

  const Icon = ICONS[state];
  return (
    <button type="button" className="icon-button copy-button" onClick={onClick} aria-label={LABELS[state]} title={LABELS[state]}>
      <Icon size="1em" />
    </button>
  );
}
