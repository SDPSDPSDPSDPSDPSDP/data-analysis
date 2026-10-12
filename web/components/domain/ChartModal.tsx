"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import { ExternalLink, X } from "lucide-react";
import RunnableCode from "@/components/domain/RunnableCode";

type Props = {
  setup: string;
  code: string;
  // Full page with this chart's examples.
  href: string;
  onClose: () => void;
};

export default function ChartModal({ setup, code, href, onClose }: Props) {
  const dialog = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    dialog.current!.showModal();
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
      <RunnableCode initialCode={code} setup={setup} />
    </dialog>
  );
}
