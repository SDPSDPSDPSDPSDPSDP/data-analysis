import { useEffect, useState, type RefObject } from "react";

// Start a run slightly before the element scrolls into view.
const RUN_AHEAD_MARGIN = "200px";

// Turns true once, when the element first comes near the viewport. Content of a closed
// <details> never intersects, so it turns true when opened.
export function useVisible(ref: RefObject<HTMLElement | null>): boolean {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return;
        setVisible(true);
        observer.disconnect();
      },
      { rootMargin: RUN_AHEAD_MARGIN },
    );
    observer.observe(ref.current!);
    return () => observer.disconnect();
  }, [ref]);
  return visible;
}
