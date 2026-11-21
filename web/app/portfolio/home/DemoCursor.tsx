"use client";

import { useEffect, useRef, useState } from "react";
import { runDemoCursor } from "./demoScript";

/** Scripted arrow for portfolio recordings: hovers charts in a loop. */
export default function DemoCursor() {
  const cursorRef = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    return runDemoCursor(cursorRef.current!, setVisible);
  }, []);

  return (
    <div ref={cursorRef} className="demo-cursor" data-visible={visible} aria-hidden="true">
      <svg viewBox="0 0 24 24">
        <path d="M4 2L4 20L9.5 15.5L12.8 21.5L15.5 20L12.2 14L19 13.5L4 2Z" strokeLinejoin="round" />
      </svg>
    </div>
  );
}
