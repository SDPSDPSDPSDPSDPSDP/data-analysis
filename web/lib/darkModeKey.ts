// Separate from darkMode.ts so the server layout can import it without pulling in React client hooks.
// Also read by the inline script in app/layout.tsx, which sets the theme before first paint.
export const STORAGE_KEY = "dark-mode";
