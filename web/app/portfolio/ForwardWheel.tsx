"use client";

import { useEffect } from "react";

/** Iframe wheel events never reach the portfolio page, which turns chapters on scroll; embedded demos don't scroll, so forward every wheel to the parent. */
export default function ForwardWheel() {
  useEffect(() => {
    if (window.parent === window) return;

    function handleWheel(event: WheelEvent) {
      if (event.ctrlKey) return;
      event.preventDefault();
      window.parent.postMessage(
        { type: "demo:wheel", deltaX: event.deltaX, deltaY: event.deltaY, deltaMode: event.deltaMode },
        "*",
      );
    }

    window.addEventListener("wheel", handleWheel, { passive: false });
    return () => window.removeEventListener("wheel", handleWheel);
  }, []);

  return null;
}
