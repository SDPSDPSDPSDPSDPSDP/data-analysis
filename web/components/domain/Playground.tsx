"use client";

import { useEffect, useRef, useState } from "react";
import CodeBlock from "@/components/ui/CodeBlock";
import PlotSection, { sectionId, type PlotSectionData, type SetupCell } from "@/components/domain/PlotSection";

export type Category = {
  title: string;
  sections: PlotSectionData[];
};

type Props = {
  setup: SetupCell[];
  categories: Category[];
  showSetup: boolean;
  // Open every "more examples" list.
  expanded: boolean;
};

export default function Playground({ setup, categories, showSetup, expanded }: Props) {
  const [setupCodes, setSetupCodes] = useState(() => setup.map((cell) => cell.code));
  // Edits apply to the examples only once a setup cell is run.
  const [setupCode, setSetupCode] = useState(() => setupCodes.join("\n\n"));
  const main = useRef<HTMLElement>(null);
  // Blocks fade in the first time they scroll into view; ones arriving together stagger.
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
    main.current!.querySelectorAll(":scope > :not(div), :scope > div > *").forEach((block) => observer.observe(block));
    return () => observer.disconnect();
  }, []);
  return (
    <main className="page" ref={main}>
      {showSetup && (
        <>
          <h2>Setup</h2>
          {setup.map((cell, i) => (
            <section key={i} className="setup-cell">
              {cell.explanation && <p>{cell.explanation}</p>}
              <CodeBlock
                value={setupCodes[i]}
                onChange={(code) => setSetupCodes((codes) => codes.map((c, j) => (j === i ? code : c)))}
                onRun={(code) => setSetupCode(setupCodes.map((c, j) => (j === i ? code : c)).join("\n\n"))}
              />
            </section>
          ))}
        </>
      )}
      {categories.map((category) => (
        <div key={category.title}>
          {category.sections.length > 1 && <h2 id={sectionId(category.title)}>{category.title}</h2>}
          {category.sections.map((section) => (
            <PlotSection
              key={section.title}
              {...section}
              globalSetup={setupCode}
              standalone={category.sections.length === 1}
              expanded={expanded}
            />
          ))}
        </div>
      ))}
    </main>
  );
}
