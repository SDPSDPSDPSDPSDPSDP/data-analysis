import type { MouseEvent } from "react";

// Ctrl/meta/shift or a non-primary button: the browser opens a new tab or window, so the page must not intercept.
export function isModifiedClick(event: MouseEvent): boolean {
  return event.ctrlKey || event.metaKey || event.shiftKey || event.button !== 0;
}
