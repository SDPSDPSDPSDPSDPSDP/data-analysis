"use client";

import { useState } from "react";
import dynamic from "next/dynamic";
import Nav, { type NavCategory } from "@/components/domain/Nav";
import ChartPreview from "@/components/domain/ChartPreview";
import { useGalleryOrder } from "@/lib/domain/useGalleryOrder";
import { sectionId, type HomeChart as Chart } from "@/lib/sections";
import { SITE_NAME } from "@/lib/site";
import { useDarkMode } from "@/lib/darkMode";
import { withDarkMode } from "@/lib/exampleSetup";

// Code editor and Python runner load on first open, not with the gallery.
const loadChartModal = () => import("@/components/domain/ChartModal");
const ChartModal = dynamic(loadChartModal, { ssr: false });

type Props = {
  categories: NavCategory[];
  charts: Chart[];
  // Nav. Off on portfolio screens: the host page frames them with its own chrome.
  showNav?: boolean;
  // Fixed chart per leading slot; null slots and everything after get the shuffled rest. `limit` caps how many show.
  pinned?: (Chart | null)[];
  limit?: number;
};

// Module-level so the default keeps one identity: a fresh `[]` per render retriggers the shuffle effect forever.
const NO_PINS: (Chart | null)[] = [];

// A failed decode still opens the modal (the img retries the load), so it resolves to the error for the caller to rethrow.
function decodeImage(src: string): Promise<unknown> {
  const image = new Image();
  image.src = src;
  return image.decode().then(
    () => null,
    (err: unknown) => err,
  );
}

export default function HomeGallery({
  categories,
  charts,
  showNav = true,
  pinned = NO_PINS,
  limit = charts.length,
}: Props) {
  const dark = useDarkMode();
  // Clicked card; the others shrink first, the modal opens once they are done.
  const [selected, setSelected] = useState<Chart | null>(null);
  // Card is the clicked one, the modal chart flies out of it.
  // Returning: modal chart is flying back, its card shows again.
  const [open, setOpen] = useState<{ chart: Chart; card: HTMLElement; returning?: boolean } | null>(null);
  const order = useGalleryOrder(charts, pinned, limit);

  // Chart flies out while the others shrink. Modal code loaded and image decoded first, so the modal
  // can measure its final size on open.
  function openChart(chart: Chart, card: HTMLElement) {
    setSelected(chart);
    const decoded = decodeImage(dark ? chart.darkPreview : chart.preview);
    Promise.all([loadChartModal(), decoded]).then(([, decodeError]) => {
      setOpen({ chart, card });
      if (decodeError) throw decodeError;
    });
  }

  return (
    <>
      {showNav && <Nav categories={categories} />}
      <main className="page home">
        <h1 className="visually-hidden">{SITE_NAME}</h1>
        <div className="home-charts">
          {order?.map((chart, index) => (
            <ChartPreview
              key={chart.code}
              src={dark ? chart.darkCardPreview : chart.cardPreview}
              title={chart.title}
              subtitle={chart.subtitle}
              index={index}
              shrunk={selected !== null && selected !== chart}
              hidden={open?.chart === chart && !open.returning}
              returning={open?.chart === chart && !!open.returning}
              onOpen={(card) => openChart(chart, card)}
            />
          ))}
        </div>
      </main>
      {open && (
        <ChartModal
          title={open.chart.title}
          setup={withDarkMode(open.chart.setup, dark)}
          code={open.chart.code}
          preview={{ light: open.chart.preview, dark: open.chart.darkPreview }}
          card={open.card}
          href={`/all#${sectionId(open.chart.section)}`}
          section={open.chart.section}
          // Other cards grow back while the chart flies, not after it lands.
          onReturn={() => {
            setOpen({ ...open, returning: true });
            setSelected(null);
          }}
          onClose={() => setOpen(null)}
        />
      )}
    </>
  );
}
