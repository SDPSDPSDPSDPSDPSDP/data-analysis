"use client";

import { useSyncExternalStore } from "react";

const subscribe = () => () => {};

// False in the prerendered HTML and during hydration, true after. Components mounted later get true right away.
export function useHydrated(): boolean {
  return useSyncExternalStore(subscribe, () => true, () => false);
}
