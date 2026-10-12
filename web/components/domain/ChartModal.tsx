"use client";

import { useLayoutEffect, useRef } from "react";
import Link from "next/link";
import { ExternalLink, X } from "lucide-react";
import RunnableCode from "@/components/domain/RunnableCode";

type Props = {
  setup: string;
  code: string;
  preview: string;
  // Spot of the card that opened the modal, the chart flies from there into place.
  origin: DOMRect;
  // Full page with this chart's examples.
  href: string;
  onClose: () => void;
};

export default function ChartModal({ setup, code, preview, origin, href, onClose }: Props) {
  const dialog = useRef<HTMLDialogElement>(null);

  // Layout effect: figure must start at the card's spot before first paint.
  // FLIP: figure laid out in place, CSS animates it from the card's rect back to it.
  useLayoutEffect(() => {
    const modal = dialog.current!;
    if (!modal.open) modal.showModal();
    const figure = modal.querySelector<HTMLElement>(".output .chart")!;
    // StrictMode runs this twice in dev: measuring while already flying would read the card's spot, not the target.
    figure.classList.remove("flying");
    const target = figure.getBoundingClientRect();
    figure.style.setProperty("--fly-x", `${origin.left - target.left}px`);
    figure.style.setProperty("--fly-y", `${origin.top - target.top}px`);
    figure.style.setProperty("--fly-scale", `${origin.width / target.width}`);
    figure.classList.add("flying");
    figure.addEventListener("animationend", () => figure.classList.remove("flying"), { once: true });
  }, []);

  return (
    <dialog
      ref={dialog}
      className="chart-modal"
      onClose={onClose}
      // Clicks on the backdrop land on the dialog itself.
      onClick={(event) => event.target === dialog.current && dialog.current.close()}
      // CodeMirror swallows Escape while the editor has focus, so the native cancel never fires.
      onKeyDown={(event) => event.key === "Escape" && dialog.current!.close()}
    >
      <div className="chart-modal-actions">
        <Link href={href} className="chart-modal-button" aria-label="Open full page">
          <ExternalLink size="1em" />
        </Link>
        <button type="button" className="chart-modal-button" onClick={() => dialog.current!.close()} aria-label="Close">
          <X size="1em" />
        </button>
      </div>
      <RunnableCode initialCode={code} setup={setup} preview={preview} />
    </dialog>
  );
}
