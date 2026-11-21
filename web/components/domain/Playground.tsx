"use client";

import { useRef, useState } from "react";
import CodeBlock from "@/components/ui/CodeBlock";
import PlotSection from "@/components/domain/PlotSection";
import { sectionId, type Category, type SetupCell } from "@/lib/sections";
import { useDarkMode } from "@/lib/darkMode";
import { useRevealOnScroll } from "@/lib/useRevealOnScroll";
import { withDarkMode } from "@/lib/exampleSetup";

type Props = {
  // Page heading for screen readers and outlines; the nav already shows it visually.
  title: string;
  setup: SetupCell[];
  categories: Category[];
  showSetup: boolean;
  // Show every example directly, no "more examples" toggle.
  expanded: boolean;
};

export default function Playground({ title, setup, categories, showSetup, expanded }: Props) {
  // Toggling dark mode edits the shown PlotGraphs(...) call and reruns the examples with it.
  const dark = useDarkMode();
  const toggle = (code: string) => (code.includes("PlotGraphs(") ? withDarkMode(code, dark) : code);
  const [setupCodes, setSetupCodes] = useState(() => setup.map((cell) => toggle(cell.code)));
  // Edits apply to the examples only once a setup cell is run.
  const [setupCode, setSetupCode] = useState(() => setupCodes.join("\n\n"));
  // Adjusted during render, not in an effect, so the examples never run once with the stale theme.
  const [codesDark, setCodesDark] = useState(dark);
  if (codesDark !== dark) {
    setCodesDark(dark);
    setSetupCodes(setupCodes.map(toggle));
    setSetupCode(toggle(setupCode));
  }
  const main = useRef<HTMLElement>(null);
  useRevealOnScroll(main);
  return (
    <main className="page" ref={main}>
      <h1 className="visually-hidden">{title}</h1>
      {showSetup && (
        <>
          <h2>Setup</h2>
          {setup.map((cell, i) => (
            <section key={i} className="setup-cell">
              {cell.explanation && <p>{cell.explanation}</p>}
              <CodeBlock
                value={setupCodes[i]}
                dark={dark}
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
