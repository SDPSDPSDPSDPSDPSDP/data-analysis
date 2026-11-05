export const FILTER = "Bar charts";
export const CARD_SELECTOR = ".home-charts .chart-preview-card";

// Synthetic events never trigger CSS :hover, so the hovered card and nav item get this attribute instead.
const HOVER_ATTR = "data-demo-hover";

export function hover(el: Element | null) {
  document.querySelectorAll(`[${HOVER_ATTR}]`).forEach((other) => other.removeAttribute(HOVER_ATTR));
  el?.setAttribute(HOVER_ATTR, "");
}

export function card(index: number) {
  const card = document.querySelectorAll(CARD_SELECTOR)[index];
  if (!card) throw new Error(`DemoCursor: no chart card at index ${index}`);
  return card;
}

export function filterButton() {
  const button = [...document.querySelectorAll(".nav-menu button")].find((el) => el.textContent === FILTER);
  if (!button) throw new Error(`DemoCursor: no "${FILTER}" filter in nav`);
  return button as HTMLButtonElement;
}
