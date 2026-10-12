"use client";

import { useState } from "react";
import Nav from "@/components/domain/Nav";
import ChartPreview from "@/components/domain/ChartPreview";

type Props = {
  categories: { title: string; sections: { title: string }[] }[];
  charts: { code: string; href: string; category: string }[];
};

export default function HomeGallery({ categories, charts }: Props) {
  const [active, setActive] = useState<string | null>(null);
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
            .map(({ code, href }) => (
              <ChartPreview key={code} code={code} href={href} />
            ))}
        </div>
      </main>
    </>
  );
}
