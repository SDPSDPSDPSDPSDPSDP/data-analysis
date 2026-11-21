"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { sectionId } from "@/lib/sections";
import SectionIcon from "@/components/domain/SectionIcon";
import { setDarkMode, useDarkMode } from "@/lib/darkMode";

type Props = {
  categories: { title: string; sections: { title: string }[] }[];
};

export default function Nav({ categories }: Props) {
  // Hover and focus keep the dropdown open after a click, so close it until the mouse leaves.
  const [dropdownClosed, setDropdownClosed] = useState(false);
  const pathname = usePathname();
  const dark = useDarkMode();
  // Tab flips the theme only while nothing has focus, so focus navigation and code editor indent keep working.
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key !== "Tab" || e.shiftKey || e.ctrlKey || e.altKey || e.metaKey) return;
      if (document.activeElement !== document.body) return;
      e.preventDefault();
      setDarkMode(document.documentElement.dataset.theme !== "dark");
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);
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
      <button
        type="button"
        className="nav-link nav-theme"
        aria-pressed={dark}
        aria-label="Dark mode"
        title="Dark mode"
        onClick={() => setDarkMode(!dark)}
      >
        {/* CSS picks the icon from data-theme, so the prerendered button already matches before hydration. */}
        <Moon size="1em" className="dark-only" aria-hidden />
        <Sun size="1em" className="light-only" aria-hidden />
      </button>
    </nav>
  );
}
