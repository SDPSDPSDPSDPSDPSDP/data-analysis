import { useMemo } from "react";
import type { HomeChart as Chart } from "@/lib/sections";
import { useHydrated } from "@/lib/useHydrated";

function shuffle<T>(items: T[]): T[] {
  for (let i = items.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [items[i], items[j]] = [items[j], items[i]];
  }
  return items;
}

// Pinned charts fill their slots, null slots and everything after get the shuffled rest, capped at `limit`.
export function useGalleryOrder(charts: Chart[], pinned: (Chart | null)[], limit: number): Chart[] | null {
  // Shuffled after hydration: static export prerenders HTML, shuffling earlier would mismatch it.
  // Grid stays empty until then, else the entrance wave starts on the unshuffled order and cards jump mid-animation.
  const hydrated = useHydrated();
  return useMemo(() => {
    if (!hydrated) return null;
    // Matched by preview path: props arrive as separate copies, and titles repeat.
    const shuffled = shuffle(charts.filter((chart) => !pinned.some((slot) => slot?.preview === chart.preview)));
    const slotted = pinned.map((chart) => chart ?? shuffled.shift()!);
    return [...slotted, ...shuffled].slice(0, limit);
  }, [hydrated, charts, pinned, limit]);
}
