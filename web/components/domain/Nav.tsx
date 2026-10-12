"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { sectionId } from "@/components/domain/PlotSection";
import SectionIcon from "@/components/domain/SectionIcon";

type Props = {
  categories: { title: string; sections: { title: string }[] }[];
};

export default function Nav({ categories }: Props) {
  // Hover and focus keep the dropdown open after a click, so close it until the mouse leaves.
  const [dropdownClosed, setDropdownClosed] = useState(false);
  // Home has no link to every example, so the brand leads there.
  const pathname = usePathname();
  return (
    <nav className="nav">
      <Link href={pathname === "/" ? "/all" : "/"} className="nav-brand">
        shirin
      </Link>
      <div className="nav-menus">
        {categories.map((category) => (
          <div
            key={category.title}
            className={dropdownClosed ? "nav-menu nav-menu-closed" : "nav-menu"}
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
    </nav>
  );
}
