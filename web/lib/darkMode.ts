
import { useSyncExternalStore } from "react";

// Also read by the inline script in app/layout.tsx, which sets the theme before first paint.
export const STORAGE_KEY = "dark-mode";
const listeners = new Set<() => void>();

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function setDarkMode(dark: boolean) {
  localStorage.setItem(STORAGE_KEY, dark ? "1" : "0");
  document.documentElement.dataset.theme = dark ? "dark" : "light";
  listeners.forEach((listener) => listener());
}

// Off during prerender, the stored choice applies after hydration.
export function useDarkMode(): boolean {
  return useSyncExternalStore(subscribe, () => localStorage.getItem(STORAGE_KEY) === "1", () => false);
}
