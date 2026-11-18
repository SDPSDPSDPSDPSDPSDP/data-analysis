import { useEffect, useState } from "react";
import type { getHomeCharts } from "@/app/homeCharts";

export type Chart = ReturnType<typeof getHomeCharts>[number];

// Pinned charts fill their slots, null slots and everything after get the shuffled rest, capped at `limit`.
export function useGalleryOrder(charts: Chart[], pinned: (Chart | null)[], limit: number): Chart[] | null {
  const [order, setOrder] = useState<Chart[] | null>(null);
  // Shuffled after mount: static export prerenders HTML, shuffling during render would mismatch hydration.
  // Grid stays empty until then, else the entrance wave starts on the unshuffled order and cards jump mid-animation.
  useEffect(() => {
    // Matched by preview path: props arrive as separate copies, and titles repeat.
    const shuffled = charts.filter((chart) => !pinned.some((slot) => slot?.preview === chart.preview));
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    const slotted = pinned.map((chart) => chart ?? shuffled.shift()!);
    setOrder([...slotted, ...shuffled].slice(0, limit));
  }, [charts, pinned, limit]);

  return order;
}
