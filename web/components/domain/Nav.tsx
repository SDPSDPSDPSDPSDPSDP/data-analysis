"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { sectionId } from "@/lib/sections";
import SectionIcon from "@/components/domain/SectionIcon";
import ThemeToggle from "@/components/domain/ThemeToggle";

export type NavCategory = { title: string; sections: { title: string }[] };

type Props = {
  categories: NavCategory[];
};

export default function Nav({ categories }: Props) {
  // Hover and focus keep the dropdown open after a click, so close it until the mouse leaves.
  const [dropdownClosed, setDropdownClosed] = useState(false);
  const pathname = usePathname();
  return (
    <nav className="nav">
      {/* Home has no link to every example, so the brand leads there. */}
      <Link href={pathname === "/" ? "/all" : "/"} className="nav-brand">
        data ink
      </Link>
      <div className="nav-menus">
        {categories.map((category) => (
          <div
            key={category.title}
            className={dropdownClosed ? "nav-menu nav-menu-closed" : "nav-menu"}
            // Layout wrapper; mouse-leave only resets the hover dropdown, keyboard users get it via :focus-within.
            role="presentation"
            onMouseLeave={() => setDropdownClosed(false)}
          >
            <Link href={`/${sectionId(category.title)}`} className="nav-link">
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
        ))}
      </div>
      <ThemeToggle />
    </nav>
  );
}
