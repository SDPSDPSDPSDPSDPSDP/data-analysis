"use client";

import { useLayoutEffect, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { X } from "lucide-react";
import RunnableCode from "@/components/domain/RunnableCode";
import SectionIcon from "@/components/domain/SectionIcon";

type Props = {
  setup: string;
  code: string;
  preview: string;
  // Spot of the card that opened the modal, the chart flies from there into place.
  origin: DOMRect;
  // Full page with this chart's examples.
  href: string;
  // Section title, names the documentation button.
  section: string;
  onClose: () => void;
};

export default function ChartModal({ setup, code, preview, origin, href, section, onClose }: Props) {
  const dialog = useRef<HTMLDialogElement>(null);
  const router = useRouter();

  // Staggered fade out, then `then`. Chart fades last, so its end is the end of the whole fade.
  // Computed times are always in seconds; reduced motion drops the animation, so they read 0.
  function leave(then: () => void) {
    const modal = dialog.current!;
    if (modal.classList.contains("closing")) return;
    modal.classList.add("closing");
    const last = getComputedStyle(modal.querySelector(".output")!);
    setTimeout(then, (parseFloat(last.animationDelay) + parseFloat(last.animationDuration)) * 1000);
  }

  const close = () => leave(() => dialog.current!.close());

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
      onClick={(event) => event.target === dialog.current && close()}
      // CodeMirror swallows Escape while the editor has focus, so the native cancel never fires.
      onKeyDown={(event) => event.key === "Escape" && close()}
      onCancel={(event) => {
        event.preventDefault();
        close();
      }}
    >
      <div className="chart-modal-actions">
        <button type="button" className="chart-modal-button" onClick={close} aria-label="Close">
          <X size="1em" />
        </button>
      </div>
      <RunnableCode initialCode={code} setup={setup} preview={preview} />
      <Link
        href={href}
        className="chart-modal-docs"
        onClick={(event) => {
          // Modified clicks open a new tab, the modal stays.
          if (event.ctrlKey || event.metaKey || event.shiftKey || event.button !== 0) return;
          event.preventDefault();
          leave(() => router.push(href));
        }}
      >
        <SectionIcon title={section} />
        <span className="chart-modal-docs-text">
          <span className="chart-modal-docs-eyebrow">Documentation</span>
          {section}
        </span>
      </Link>
    </dialog>
  );
}
