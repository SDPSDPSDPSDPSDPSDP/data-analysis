"use client";

import { useState } from "react";
import { ChartColumn } from "lucide-react";
import CodeBlock from "@/components/ui/CodeBlock";
import RunnableCode from "@/components/domain/RunnableCode";

type SetupCell = {
  explanation: string;
  code: string;
};

type Props = {
  title: string;
  setup: SetupCell[];
  examples: string[];
};

export default function Playground({ title, setup, examples }: Props) {
  const setupCode = setup.map((cell) => cell.code).join("\n\n");
  const titleId = title.toLowerCase().replace(/\s+/g, "-");
  // Hover and focus keep the dropdown open after a click, so close it until the mouse leaves.
  const [dropdownClosed, setDropdownClosed] = useState(false);
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
            <a
              href={`#${titleId}`}
              onClick={(e) => {
                e.currentTarget.blur();
                setDropdownClosed(true);
              }}
            >
              {title}
            </a>
          </div>
        </div>
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
        <h3 id={titleId}>{title}</h3>
        {examples.map((code, i) => (
          <RunnableCode key={i} initialCode={code} setup={setupCode} />
        ))}
      </main>
    </>
  );
}
