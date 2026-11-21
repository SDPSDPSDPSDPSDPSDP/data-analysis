"use client";

import { useEffect, useRef, useState } from "react";
import { createDemoClock } from "./demoClock";
import { CARD_SELECTOR, card, hover } from "./demoTargets";

type Point = { x: number; y: number };

// Grid positions to hover: spread out so the arrow crosses the page.
const HOVERS = [0, 6, 9, 1, 4, 2];
const TRAVEL_MS = 700;
const DWELL_MS = 1100;
// Grid fades in with its stagger before the arrow appears.
const SETTLE_MS = 1800;
// Reader's own pointer pauses the script until it rests this long.
const IDLE_RESUME_MS = 3000;

/** Scripted arrow for portfolio recordings: hovers charts in a loop. */
export default function DemoCursor() {
  const cursorRef = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const controller = new AbortController();
    const { signal } = controller;
    const clock = createDemoClock(signal);
    const { frame, wait } = clock;
    let idleTimer: ReturnType<typeof setTimeout> | undefined;
    let current: Point = { x: innerWidth / 2, y: innerHeight };

    function moveTo(point: Point) {
      current = point;
      cursorRef.current!.style.transform = `translate(calc(${point.x}px - var(--demo-cursor-tip-x)), calc(${point.y}px - var(--demo-cursor-tip-y)))`;
    }

    async function travel(el: Element) {
      const rect = el.getBoundingClientRect();
      const from = current;
      const to = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
      await wait(TRAVEL_MS, (t) => {
        const eased = t * t * (3 - 2 * t);
        moveTo({ x: from.x + (to.x - from.x) * eased, y: from.y + (to.y - from.y) * eased });
      });
      hover(el);
    }

    async function hoverCards(indexes: number[]) {
      for (const index of indexes) {
        await travel(card(index));
        await wait(DWELL_MS);
      }
    }

    async function run() {
      // Grid shuffles after mount, cards appear once it has.
      while (!document.querySelector(CARD_SELECTOR)) await frame();
      await wait(SETTLE_MS);
      moveTo(current);
      setVisible(true);
      while (true) await hoverCards(HOVERS);
    }

    function onRealPointer(event: PointerEvent) {
      if (!event.isTrusted) return;
      clock.paused = true;
      setVisible(false);
      hover(null);
      clearTimeout(idleTimer);
      idleTimer = setTimeout(() => {
        clock.paused = false;
        setVisible(true);
      }, IDLE_RESUME_MS);
    }

    addEventListener("pointermove", onRealPointer, { passive: true });
    run().catch((error) => {
      if (!signal.aborted) throw error;
    });

    return () => {
      controller.abort();
      clearTimeout(idleTimer);
      removeEventListener("pointermove", onRealPointer);
      hover(null);
    };
  }, []);

  return (
    <div ref={cursorRef} className="demo-cursor" data-visible={visible} aria-hidden="true">
      <svg viewBox="0 0 24 24">
        <path d="M4 2L4 20L9.5 15.5L12.8 21.5L15.5 20L12.2 14L19 13.5L4 2Z" strokeLinejoin="round" />
      </svg>
    </div>
  );
}
