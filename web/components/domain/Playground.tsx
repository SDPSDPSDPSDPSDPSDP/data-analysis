"use client";

import { useState } from "react";
import { ChartColumn, ChevronsDownUp, ChevronsUpDown } from "lucide-react";
import CodeBlock from "@/components/ui/CodeBlock";
import PlotSection, { sectionId, type PlotSectionData, type SetupCell } from "@/components/domain/PlotSection";

type Props = {
  setup: SetupCell[];
  sections: PlotSectionData[];
};

export default function Playground({ setup, sections }: Props) {
  const setupCode = setup.map((cell) => cell.code).join("\n\n");
  // Hover and focus keep the dropdown open after a click, so close it until the mouse leaves.
  const [dropdownClosed, setDropdownClosed] = useState(false);
  const [expandAll, setExpandAll] = useState(false);
  return (
    <>
      <nav className="nav">
        <a href="#" className="nav-brand">
          shirin
        </a>
        <div
          className={dropdownClosed ? "nav-menu nav-menu-closed" : "nav-menu"}
          onMouseLeave={() => setDropdownClosed(false)}
        >
          <a href="#bar-charts" className="nav-link">
            <ChartColumn size="1em" aria-hidden />
            Bar charts
          </a>
          <div className="nav-dropdown">
            {sections.map((section) => (
              <a
                key={section.title}
                href={`#${sectionId(section.title)}`}
                onClick={(e) => {
                  e.currentTarget.blur();
                  setDropdownClosed(true);
                }}
              >
                {section.title}
              </a>
            ))}
          </div>
        </div>
        <label className="switch" title={expandAll ? "Collapse examples" : "Expand all examples"}>
          <input
            type="checkbox"
            role="switch"
            aria-label="Expand all examples"
            checked={expandAll}
            onChange={(e) => setExpandAll(e.target.checked)}
          />
          <span className="switch-track" aria-hidden>
            <ChevronsDownUp size="1em" />
            <ChevronsUpDown size="1em" />
            <span className="switch-knob">
              {expandAll ? <ChevronsUpDown size="1em" /> : <ChevronsDownUp size="1em" />}
            </span>
          </span>
        </label>
      </nav>
      <main className="page">
        <h2>Setup</h2>
        {setup.map((cell, i) => (
          <section key={i} className="setup-cell">
            <p>{cell.explanation}</p>
            <CodeBlock value={cell.code} />
          </section>
        ))}
        <h2 id="bar-charts">Bar charts</h2>
        {sections.map((section) => (
          <PlotSection key={section.title} {...section} globalSetup={setupCode} expandAll={expandAll} />
        ))}
      </main>
    </>
  );
}
