import { useEffect, useState, type RefObject } from "react";

// Turns true once, when the element first comes near the viewport. Default margin starts a run slightly
// before it scrolls into view. Content of a closed <details> never intersects, so it turns true when opened.
export function useVisible(ref: RefObject<HTMLElement | null>, rootMargin = "200px"): boolean {
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) return;
        setVisible(true);
        observer.disconnect();
      },
      { rootMargin },
    );
    observer.observe(ref.current!);
    return () => observer.disconnect();
  }, [ref, rootMargin]);
  return visible;
}
