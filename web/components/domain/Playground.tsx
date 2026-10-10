"use client";

import { useState } from "react";
import {
  ChartArea,
  ChartBarBig,
  ChartColumn,
  ChartPie,
  ChevronsDownUp,
  ChevronsUpDown,
  Tally5,
  type LucideIcon,
} from "lucide-react";
import CodeBlock from "@/components/ui/CodeBlock";
import PlotSection, { sectionId, type PlotSectionData, type SetupCell } from "@/components/domain/PlotSection";

// Keyed by category or section title: icon components can't be passed from the server page.
const NAV_ICONS: Record<string, LucideIcon> = {
  "Bar charts": ChartColumn,
  Countplots: Tally5,
  Barplots: ChartBarBig,
  Histograms: ChartArea,
  "Pie charts": ChartPie,
};

type Category = {
  title: string;
  sections: PlotSectionData[];
};

type Props = {
  setup: SetupCell[];
  categories: Category[];
};

function NavIcon({ title }: { title: string }) {
  const Icon = NAV_ICONS[title];
  if (!Icon) throw new Error(`No nav icon for "${title}"`);
  return <Icon size="1em" aria-hidden />;
}

export default function Playground({ setup, categories }: Props) {
  const [setupCodes, setSetupCodes] = useState(() => setup.map((cell) => cell.code));
  // Edits apply to the examples only once a setup cell is run.
  const [setupCode, setSetupCode] = useState(() => setupCodes.join("\n\n"));
  // Hover and focus keep the dropdown open after a click, so close it until the mouse leaves.
  const [dropdownClosed, setDropdownClosed] = useState(false);
  const [expandAll, setExpandAll] = useState(false);
  return (
    <>
      <nav className="nav">
        <a href="#" className="nav-brand">
          shirin
        </a>
        <div className="nav-menus">
          {categories.map((category) => (
            <div
              key={category.title}
              className={dropdownClosed ? "nav-menu nav-menu-closed" : "nav-menu"}
              onMouseLeave={() => setDropdownClosed(false)}
            >
              <a href={`#${sectionId(category.title)}`} className="nav-link">
                <NavIcon title={category.title} />
                {category.title}
              </a>
              {category.sections.length > 1 && (
                <div className="nav-dropdown">
                  {category.sections.map((section) => (
                    <a
                      key={section.title}
                      href={`#${sectionId(section.title)}`}
                      className="nav-link"
                      onClick={(e) => {
                        e.currentTarget.blur();
                        setDropdownClosed(true);
                      }}
                    >
                      <NavIcon title={section.title} />
                      {section.title}
                    </a>
                  ))}
                </div>
              )}
            </div>
          ))}
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
            <CodeBlock
              value={setupCodes[i]}
              onChange={(code) => setSetupCodes((codes) => codes.map((c, j) => (j === i ? code : c)))}
              onRun={(code) => setSetupCode(setupCodes.map((c, j) => (j === i ? code : c)).join("\n\n"))}
            />
          </section>
        ))}
        {categories.map((category) => (
          <div key={category.title}>
            {category.sections.length > 1 && <h2 id={sectionId(category.title)}>{category.title}</h2>}
            {category.sections.map((section) => (
              <PlotSection
                key={section.title}
                {...section}
                globalSetup={setupCode}
                expandAll={expandAll}
                standalone={category.sections.length === 1}
              />
            ))}
          </div>
        ))}
      </main>
    </>
  );
}
