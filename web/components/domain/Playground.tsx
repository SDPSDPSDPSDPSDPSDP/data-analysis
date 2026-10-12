"use client";

import { useState } from "react";
import CodeBlock from "@/components/ui/CodeBlock";
import PlotSection, { sectionId, type PlotSectionData, type SetupCell } from "@/components/domain/PlotSection";
import SectionIcon from "@/components/domain/SectionIcon";

type Category = {
  title: string;
  sections: PlotSectionData[];
};

type Props = {
  setup: SetupCell[];
  categories: Category[];
};

export default function Playground({ setup, categories }: Props) {
  const [setupCodes, setSetupCodes] = useState(() => setup.map((cell) => cell.code));
  // Edits apply to the examples only once a setup cell is run.
  const [setupCode, setSetupCode] = useState(() => setupCodes.join("\n\n"));
  // Hover and focus keep the dropdown open after a click, so close it until the mouse leaves.
  const [dropdownClosed, setDropdownClosed] = useState(false);
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
                <SectionIcon title={category.title} />
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
                      <SectionIcon title={section.title} />
                      {section.title}
                    </a>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </nav>
      <main className="page">
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
        {categories.map((category) => (
          <div key={category.title}>
            {category.sections.length > 1 && <h2 id={sectionId(category.title)}>{category.title}</h2>}
            {category.sections.map((section) => (
              <PlotSection
                key={section.title}
                {...section}
                globalSetup={setupCode}
                standalone={category.sections.length === 1}
              />
            ))}
          </div>
        ))}
      </main>
    </>
  );
}
