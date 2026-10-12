"use client";

import { useEffect, useState } from "react";
import Nav from "@/components/domain/Nav";
import ChartPreview from "@/components/domain/ChartPreview";
import ChartModal from "@/components/domain/ChartModal";
import { sectionId } from "@/components/domain/PlotSection";

type Chart = { setup: string; code: string; preview: string; category: string; section: string };

type Props = {
  categories: { title: string; sections: { title: string }[] }[];
  charts: Chart[];
};

export default function HomeGallery({ categories, charts }: Props) {
  const [active, setActive] = useState<string | null>(null);
  const [open, setOpen] = useState<Chart | null>(null);
  const [order, setOrder] = useState(charts);
  // Shuffled after mount: static export prerenders HTML, shuffling during render would mismatch hydration.
  useEffect(() => {
    const shuffled = [...charts];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    setOrder(shuffled);
  }, [charts]);
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
        <div className="home-charts">
          {order
            .filter((chart) => !active || chart.category === active)
            .map((chart) => (
              <ChartPreview key={chart.code} src={chart.preview} onOpen={() => setOpen(chart)} />
            ))}
        </div>
      </main>
      {open && (
        <ChartModal
          setup={open.setup}
          code={open.code}
          href={`${active ? `/${sectionId(active)}` : "/all"}#${sectionId(open.section)}`}
          onClose={() => setOpen(null)}
        />
      )}
    </>
  );
}
