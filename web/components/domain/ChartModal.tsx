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

  const figure = () => dialog.current!.querySelector<HTMLElement>(".output .chart")!;

  // FLIP: figure laid out in place, CSS animates it between the card's rect and its own.
  // Measuring while already flying would read the card's spot, not the target, so the flight is dropped first.
  function aim(chart: HTMLElement) {
    chart.classList.remove("flying");
    const target = chart.getBoundingClientRect();
    chart.style.setProperty("--fly-x", `${origin.left - target.left}px`);
    chart.style.setProperty("--fly-y", `${origin.top - target.top}px`);
    chart.style.setProperty("--fly-scale", `${origin.width / target.width}`);
    chart.classList.add("flying");
  }

  // Runs the closing animation (CSS picks it by `kind`), then `then` once the slowest part, the chart, is done.
  // Computed times are always in seconds; reduced motion drops the animation, so they read 0.
  function leave(kind: "to-card" | "to-docs", then: () => void) {
    const modal = dialog.current!;
    if (modal.classList.contains("closing")) return;
    if (kind === "to-card") aim(figure());
    modal.classList.add("closing", kind);
    const last = getComputedStyle(kind === "to-card" ? figure() : modal.querySelector(".output")!);
    setTimeout(then, (parseFloat(last.animationDelay) + parseFloat(last.animationDuration)) * 1000);
  }

  // Reverse of opening: chart flies back into its card.
  const close = () => leave("to-card", () => dialog.current!.close());

  // Layout effect: figure must start at the card's spot before first paint.
  useLayoutEffect(() => {
    const modal = dialog.current!;
    if (!modal.open) modal.showModal();
    const chart = figure();
    // StrictMode runs this twice in dev, aim drops the first flight.
    aim(chart);
    // A close mid-flight reuses the class for the way back, it must stay on.
    chart.addEventListener("animationend", () => modal.classList.contains("closing") || chart.classList.remove("flying"), {
      once: true,
    });
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
          leave("to-docs", () => router.push(href));
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
