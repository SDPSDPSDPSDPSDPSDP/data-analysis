"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { sectionId } from "@/components/domain/PlotSection";
import SectionIcon from "@/components/domain/SectionIcon";

type Props = {
  categories: { title: string; sections: { title: string }[] }[];
  // Home only: these categories filter the page instead of linking to their own page.
  filter?: {
    categories: string[];
    active: string | null;
    onSelect: (title: string) => void;
  };
};

export default function Nav({ categories, filter }: Props) {
  // Hover and focus keep the dropdown open after a click, so close it until the mouse leaves.
  const [dropdownClosed, setDropdownClosed] = useState(false);
  // Home has no link to every example, so the brand leads there, unless a filter is on: then it clears the filter.
  const pathname = usePathname();
  return (
    <nav className="nav">
      <Link
        href={pathname === "/" && !filter?.active ? "/all" : "/"}
        className="nav-brand"
        onClick={(e) => {
          if (!filter?.active) return;
          e.preventDefault();
          // Selecting the active category again clears the filter.
          filter.onSelect(filter.active);
        }}
      >
        shirin
      </Link>
      <div className="nav-menus">
        {categories.map((category) =>
          filter?.categories.includes(category.title) ? (
            <div key={category.title} className="nav-menu">
              <button
                type="button"
                className={
                  filter.active && filter.active !== category.title
                    ? "nav-link nav-link-inactive"
                    : "nav-link"
                }
                aria-pressed={filter.active === category.title}
                onClick={() => filter.onSelect(category.title)}
              >
                <SectionIcon title={category.title} />
                {category.title}
              </button>
            </div>
          ) : (
            <div
              key={category.title}
              className={
                dropdownClosed ? "nav-menu nav-menu-closed" : "nav-menu"
              }
              onMouseLeave={() => setDropdownClosed(false)}
            >
              <Link
                href={`/${sectionId(category.title)}`}
                className={filter?.active ? "nav-link nav-link-inactive" : "nav-link"}
              >
                <SectionIcon title={category.title} />
                {category.title}
              </Link>
              {category.sections.length > 1 && (
                <div className="nav-dropdown">
                  {category.sections.map((section) => (
                    <Link
                      key={section.title}
                      href={`/${sectionId(category.title)}#${sectionId(section.title)}`}
                      className="nav-link"
                      onClick={(e) => {
                        e.currentTarget.blur();
                        setDropdownClosed(true);
                      }}
                    >
                      <SectionIcon title={section.title} />
                      {section.title}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ),
        )}
      </div>
    </nav>
  );
}
