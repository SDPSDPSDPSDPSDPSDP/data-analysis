"use client";

import { useState } from "react";
import { ChartArea, ChartColumn, ChevronsDownUp, ChevronsUpDown, type LucideIcon } from "lucide-react";
import CodeBlock from "@/components/ui/CodeBlock";
import PlotSection, { sectionId, type PlotSectionData, type SetupCell } from "@/components/domain/PlotSection";

// Keyed by title: icon components can't be passed from the server page.
const CATEGORY_ICONS: Record<string, LucideIcon> = {
  "Bar charts": ChartColumn,
  Distributions: ChartArea,
};

type Category = {
  title: string;
  sections: PlotSectionData[];
};

type Props = {
  setup: SetupCell[];
  categories: Category[];
};

function categoryIcon(title: string): LucideIcon {
  const icon = CATEGORY_ICONS[title];
  if (!icon) throw new Error(`No icon for category "${title}"`);
  return icon;
}

export default function Playground({ setup, categories }: Props) {
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
        <div className="nav-menus">
          {categories.map((category) => {
            const Icon = categoryIcon(category.title);
            return (
              <div
                key={category.title}
                className={dropdownClosed ? "nav-menu nav-menu-closed" : "nav-menu"}
                onMouseLeave={() => setDropdownClosed(false)}
              >
                <a href={`#${sectionId(category.title)}`} className="nav-link">
                  <Icon size="1em" aria-hidden />
                  {category.title}
                </a>
                <div className="nav-dropdown">
                  {category.sections.map((section) => (
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
            );
          })}
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
        {categories.map((category) => (
          <div key={category.title}>
            <h2 id={sectionId(category.title)}>{category.title}</h2>
            {category.sections.map((section) => (
              <PlotSection key={section.title} {...section} globalSetup={setupCode} expandAll={expandAll} />
            ))}
          </div>
        ))}
      </main>
    </>
  );
}
