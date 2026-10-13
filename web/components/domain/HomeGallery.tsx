"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Nav from "@/components/domain/Nav";
import ChartPreview from "@/components/domain/ChartPreview";
import ChartModal from "@/components/domain/ChartModal";
import { sectionId } from "@/components/domain/PlotSection";
import type { getHomeCharts } from "@/app/categories";

type Chart = ReturnType<typeof getHomeCharts>[number];

type Props = {
  categories: { title: string; sections: { title: string }[] }[];
  charts: Chart[];
  // Off on portfolio screens: the host page frames them with its own chrome.
  showNav?: boolean;
  // Fixed chart per leading slot; null slots and everything after get the shuffled rest. `limit` caps how many show.
  pinned?: (Chart | null)[];
  limit?: number;
};

export default function HomeGallery({ categories, charts, showNav = true, pinned = [], limit = charts.length }: Props) {
  const router = useRouter();
  const [active, setActive] = useState<string | null>(null);
  // Clicked card; the others shrink first, the modal opens once they are done.
  const [selected, setSelected] = useState<Chart | null>(null);
  // Origin is the clicked card's spot, the modal chart flies out of it.
  // Returning: modal chart is flying back, its card shows again.
  const [open, setOpen] = useState<{ chart: Chart; origin: DOMRect; returning?: boolean } | null>(null);
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

  // Set while switching filter: every card shrinks away before the new ones fade in.
  const [leaving, setLeaving] = useState(false);

  // Computed transitionDuration is always in seconds; the raw token may be minified to another unit.
  function shrinkAll(then: () => void) {
    setLeaving(true);
    const card = document.querySelector(".chart-preview");
    setTimeout(then, card ? parseFloat(getComputedStyle(card).transitionDuration) * 1000 : 0);
  }

  // Chart flies out while the others shrink. Modal image decoded first so the modal can measure its final size on open.
  function openChart(chart: Chart, card: HTMLElement) {
    setSelected(chart);
    const image = new Image();
    image.src = chart.preview;
    image.decode().then(() => setOpen({ chart, origin: card.querySelector(".chart-preview-card")!.getBoundingClientRect() }));
  }

  function selectFilter(next: string | null) {
    shrinkAll(() => {
      setActive(next);
      setLeaving(false);
    });
  }

  return (
    <>
      {showNav && (
        <Nav
          categories={categories}
          filter={{
            categories: [...new Set(charts.map((chart) => chart.category))],
            active,
            // Clicking the active category again shows every chart.
            onSelect: (title) => selectFilter(title === active ? null : title),
            onLeave: (href) => shrinkAll(() => router.push(href)),
          }}
        />
      )}
      <main className="page home">
        {/* Keyed on filter so the entrance wave replays on every category switch. */}
        <div className="home-charts" key={active ?? ""}>
          {order
            ?.filter((chart) => !active || chart.category === active)
            .map((chart, index) => (
              <ChartPreview
                key={chart.code}
                src={chart.cardPreview}
                title={chart.title}
                subtitle={chart.subtitle}
                index={index}
                shrunk={leaving || (selected !== null && selected !== chart)}
                hidden={open?.chart === chart && !open.returning}
                returning={open?.chart === chart && !!open.returning}
                onOpen={(card) => openChart(chart, card)}
              />
            ))}
        </div>
      </main>
      {open && (
        <ChartModal
          setup={open.chart.setup}
          code={open.chart.code}
          preview={open.chart.preview}
          origin={open.origin}
          href={`${active ? `/${sectionId(active)}` : "/all"}#${sectionId(open.chart.section)}`}
          section={open.chart.section}
          onReturn={() => setOpen({ ...open, returning: true })}
          onClose={() => {
            setOpen(null);
            setSelected(null);
          }}
        />
      )}
    </>
  );
}
