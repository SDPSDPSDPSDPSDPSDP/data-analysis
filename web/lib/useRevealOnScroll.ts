import { useEffect, type RefObject } from "react";

// Blocks of ref (children, and children of its div wrappers) fade in (class `seen`) the first time they scroll into view; ones arriving together stagger.
export function useRevealOnScroll(ref: RefObject<HTMLElement | null>): void {
  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries
        .filter((entry) => entry.isIntersecting)
        .forEach((entry, i) => {
          const block = entry.target as HTMLElement;
          block.style.setProperty("--i", `${i}`);
          block.classList.add("seen");
          observer.unobserve(block);
        });
    });
    ref.current!.querySelectorAll(":scope > :not(div), :scope > div > *").forEach((block) => observer.observe(block));
    return () => observer.disconnect();
  }, [ref]);
}
