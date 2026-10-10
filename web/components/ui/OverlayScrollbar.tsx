"use client";

import { useEffect, useRef } from "react";

function scrollerOf(el: Element | null): Element {
  const root = document.documentElement;
  for (; el && el !== root; el = el.parentElement) {
    const { overflowY } = getComputedStyle(el);
    if ((overflowY === "auto" || overflowY === "scroll") && el.scrollHeight > el.clientHeight) return el;
  }
  return root;
}

// Native scrollbars are hidden in globals.css; CSS alone cannot draw one over content.
export default function OverlayScrollbar() {
  const thumbRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = document.documentElement;
    const thumb = thumbRef.current!;
    let target: Element = root;

    function hide() {
      thumb.style.opacity = "0";
    }

    function draw() {
      const { scrollTop, scrollHeight, clientHeight } = target;
      if (scrollHeight <= clientHeight) return hide();
      const box = target === root ? { top: 0, right: root.clientWidth } : target.getBoundingClientRect();
      const height = (clientHeight * clientHeight) / scrollHeight;
      const top = box.top + (scrollTop / (scrollHeight - clientHeight)) * (clientHeight - height);
      thumb.style.top = `${top}px`;
      thumb.style.left = `${box.right}px`;
      thumb.style.height = `${height}px`;
      thumb.style.opacity = "1";
    }

    function onOver(e: PointerEvent) {
      target = scrollerOf(e.target as Element);
      draw();
    }

    function onScroll(e: Event) {
      const el = e.target === document ? root : e.target;
      if (el === target) draw();
    }

    document.addEventListener("pointerover", onOver);
    document.addEventListener("scroll", onScroll, true);
    root.addEventListener("mouseleave", hide);
    return () => {
      document.removeEventListener("pointerover", onOver);
      document.removeEventListener("scroll", onScroll, true);
      root.removeEventListener("mouseleave", hide);
    };
  }, []);

  return <div ref={thumbRef} className="overlay-scrollbar" aria-hidden />;
}
