"use client";

import { useState } from "react";
import Nav from "@/components/domain/Nav";
import ChartPreview from "@/components/domain/ChartPreview";
import ChartModal from "@/components/domain/ChartModal";
import { sectionId } from "@/components/domain/PlotSection";

type Chart = { setup: string; code: string; category: string };

type Props = {
  categories: { title: string; sections: { title: string }[] }[];
  charts: Chart[];
};

export default function HomeGallery({ categories, charts }: Props) {
  const [active, setActive] = useState<string | null>(null);
  const [open, setOpen] = useState<Chart | null>(null);
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
          {charts
            .filter((chart) => !active || chart.category === active)
            .map((chart) => (
              <ChartPreview key={chart.code} setup={chart.setup} code={chart.code} onOpen={() => setOpen(chart)} />
            ))}
        </div>
      </main>
      {open && (
        <ChartModal
          setup={open.setup}
          code={open.code}
          href={active ? `/${sectionId(active)}` : "/all"}
          onClose={() => setOpen(null)}
        />
      )}
    </>
  );
}
