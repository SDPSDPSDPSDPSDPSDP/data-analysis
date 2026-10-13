"use client";

import { useEffect, useRef, useState } from "react";

type Point = { x: number; y: number };

const FILTER = "Bar charts";
// Grid positions to hover, before and after filtering: spread out so the arrow crosses the page.
const HOVERS_ALL = [0, 6, 9];
const HOVERS_FILTERED = [1, 4, 2];
const TRAVEL_MS = 700;
const DWELL_MS = 1100;
const PRESS_MS = 150;
// Filter switch: cards shrink away, then the new grid fades in with its stagger.
const SETTLE_MS = 1800;
// Reader's own pointer pauses the script until it rests this long.
const IDLE_RESUME_MS = 3000;

// Synthetic events never trigger CSS :hover, so the hovered card and nav item get this attribute instead.
const HOVER_ATTR = "data-demo-hover";

/** Scripted arrow for portfolio recordings: hovers charts, filters to bar charts, hovers, clears the filter, repeats. */
export default function DemoCursor() {
  const cursorRef = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);
  const [pressed, setPressed] = useState(false);

  useEffect(() => {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const controller = new AbortController();
    const { signal } = controller;
    let paused = false;
    let idleTimer: ReturnType<typeof setTimeout> | undefined;
    let current: Point = { x: innerWidth / 2, y: innerHeight };

    const frame = () =>
      new Promise<void>((resolve, reject) => {
        if (signal.aborted) return reject(signal.reason);
        requestAnimationFrame(() => resolve());
      });

    // Time spent paused does not count, so a reader taking over never skips a step.
    async function wait(ms: number) {
      let left = ms;
      let last = performance.now();
      while (left > 0) {
        await frame();
        const now = performance.now();
        if (!paused) left -= now - last;
        last = now;
      }
    }

    function moveTo(point: Point) {
      current = point;
      cursorRef.current!.style.transform =
        `translate(calc(${point.x}px - var(--demo-cursor-tip-x)), calc(${point.y}px - var(--demo-cursor-tip-y)))`;
    }

    function hover(el: Element | null) {
      document.querySelectorAll(`[${HOVER_ATTR}]`).forEach((other) => other.removeAttribute(HOVER_ATTR));
      el?.setAttribute(HOVER_ATTR, "");
    }

    async function travel(el: Element) {
      const rect = el.getBoundingClientRect();
      const from = current;
      const to = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
      let elapsed = 0;
      let last = performance.now();
      while (elapsed < TRAVEL_MS) {
        await frame();
        const now = performance.now();
        if (!paused) elapsed += now - last;
        last = now;
        const t = Math.min(1, elapsed / TRAVEL_MS);
        const eased = t * t * (3 - 2 * t);
        moveTo({ x: from.x + (to.x - from.x) * eased, y: from.y + (to.y - from.y) * eased });
      }
      hover(el);
    }

    function card(index: number) {
      const card = document.querySelectorAll(".home-charts .chart-preview-card")[index];
      if (!card) throw new Error(`DemoCursor: no chart card at index ${index}`);
      return card;
    }

    function filterButton() {
      const button = [...document.querySelectorAll(".nav-menu button")].find((el) => el.textContent === FILTER);
      if (!button) throw new Error(`DemoCursor: no "${FILTER}" filter in nav`);
      return button as HTMLButtonElement;
    }

    async function hoverCards(indexes: number[]) {
      for (const index of indexes) {
        await travel(card(index));
        await wait(DWELL_MS);
      }
    }

    async function clickFilter() {
      const button = filterButton();
      await travel(button.closest(".nav-menu")!);
      await wait(DWELL_MS / 2);
      setPressed(true);
      await wait(PRESS_MS);
      button.click();
      setPressed(false);
      hover(null);
      await wait(SETTLE_MS);
    }

    async function run() {
      // Grid shuffles after mount, cards appear once it has.
      while (!document.querySelector(".home-charts .chart-preview-card")) await frame();
      await wait(SETTLE_MS);
      moveTo(current);
      setVisible(true);
      while (true) {
        await hoverCards(HOVERS_ALL);
        await clickFilter();
        await hoverCards(HOVERS_FILTERED);
        await clickFilter();
      }
    }

    function onRealPointer(event: PointerEvent) {
      if (!event.isTrusted) return;
      paused = true;
      setVisible(false);
      hover(null);
      clearTimeout(idleTimer);
      idleTimer = setTimeout(() => {
        paused = false;
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
      <svg viewBox="0 0 24 24" data-pressed={pressed}>
        <path d="M4 2L4 20L9.5 15.5L12.8 21.5L15.5 20L12.2 14L19 13.5L4 2Z" strokeLinejoin="round" />
      </svg>
    </div>
  );
}
