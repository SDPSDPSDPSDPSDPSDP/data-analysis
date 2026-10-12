"use client";

import { useEffect, useState } from "react";
import { flushSync } from "react-dom";
import Nav from "@/components/domain/Nav";
import ChartPreview from "@/components/domain/ChartPreview";
import ChartModal from "@/components/domain/ChartModal";
import { sectionId } from "@/components/domain/PlotSection";
import type { getHomeCharts } from "@/app/categories";

type Chart = ReturnType<typeof getHomeCharts>[number];

type Props = {
  categories: { title: string; sections: { title: string }[] }[];
  charts: Chart[];
};

export default function HomeGallery({ categories, charts }: Props) {
  const [active, setActive] = useState<string | null>(null);
  const [open, setOpen] = useState<Chart | null>(null);
  const [order, setOrder] = useState<Chart[] | null>(null);
  // Shuffled after mount: static export prerenders HTML, shuffling during render would mismatch hydration.
  // Grid stays empty until then, else the entrance wave starts on the unshuffled order and cards jump mid-animation.
  useEffect(() => {
    const shuffled = [...charts];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    setOrder(shuffled);
  }, [charts]);

  // View transition morphs the clicked card into the modal chart, both share one view-transition-name.
  function openChart(chart: Chart, card: HTMLElement) {
    if (!document.startViewTransition) return setOpen(chart);
    card.style.viewTransitionName = "chart-hero";
    document.startViewTransition(() => {
      card.style.viewTransitionName = "";
      flushSync(() => setOpen(chart));
    });
  }
  return (
    <>
      <Nav
        categories={categories}
        filter={{
          categories: [...new Set(charts.map((chart) => chart.category))],
          active,
          // Clicking the active category again shows every chart.
          onSelect: (title) => setActive(title === active ? null : title),
        }}
      />
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
                onOpen={(card) => openChart(chart, card)}
              />
            ))}
        </div>
      </main>
      {open && (
        <ChartModal
          setup={open.setup}
          code={open.code}
          preview={open.preview}
          href={`${active ? `/${sectionId(active)}` : "/all"}#${sectionId(open.section)}`}
          onClose={() => setOpen(null)}
        />
      )}
    </>
  );
}
