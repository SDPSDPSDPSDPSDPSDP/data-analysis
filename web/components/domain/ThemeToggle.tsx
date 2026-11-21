"use client";

import { useEffect } from "react";
import { Moon, Sun } from "lucide-react";
import { setDarkMode, useDarkMode } from "@/lib/darkMode";

export default function ThemeToggle() {
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
  );
}
