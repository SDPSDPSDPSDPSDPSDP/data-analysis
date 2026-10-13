"use client";

import { useSyncExternalStore } from "react";
import { flushSync } from "react-dom";
import { STORAGE_KEY } from "./darkModeKey";

const listeners = new Set<() => void>();

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function setDarkMode(dark: boolean) {
  const apply = () => {
    localStorage.setItem(STORAGE_KEY, dark ? "1" : "0");
    document.documentElement.dataset.theme = dark ? "dark" : "light";
    // Sync so the view transition snapshots the re-rendered charts, not the old ones.
    flushSync(() => listeners.forEach((listener) => listener()));
  };
  if (document.startViewTransition) document.startViewTransition(apply);
  else apply();
}

// Off during prerender, the stored choice applies after hydration.
export function useDarkMode(): boolean {
  return useSyncExternalStore(subscribe, () => localStorage.getItem(STORAGE_KEY) === "1", () => false);
}
