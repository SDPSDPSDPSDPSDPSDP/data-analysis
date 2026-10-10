# Coding Standards & Conventions

Code structure, design tokens and conventions for the `shirin` Python package and the `web/` playground.

---

## 1. Python Package (`shirin/`)

* **Layout:** Follow the layers in [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md#architecture). New chart = public method in `plot/graphs/`, Options dataclass in `plot/core/`, plot class in `plot/plots/`. Shared helpers go in `plot/common/`, constants and palettes in `plot/config/`.
* **Options validation:** Validate user input in the Options dataclasses, not inside drawing code.
* **Matplotlib state:** Each plot draws on its own figure. Styling goes through `plt.rc_context`; never mutate global `rcParams`.
* **Python version:** Code must run on Python 3.9 (CI matrix 3.9-3.13). No `X | Y` unions at runtime, no `match` statements.
* **Number formatting:** Use `shirin/number_format.py` for Dutch formatting. Do not reformat numbers ad hoc.
* **Tests:** One `tests/test_<module>.py` per area. Run with `uv run python -m pytest`.

---

## 2. Web Component Architecture (`web/`)

* **`web/components/ui/`:** Domain-agnostic primitives (buttons, panes, tooltips). Controlled purely via generic props. Never import Pyodide or chart logic.
* **`web/components/domain/`:** Feature components (playground, editor, chart output). Compose primitives from `web/components/ui/`.
* **Python bridge:** `web/lib/pyodide.ts` is the only module that talks to `public/pyodide.worker.mjs`.
* **Component Splitting & Co-location:** When a component grows, split sub-components into a kebab-case folder containing the parent, children, and style module together:
  ```
  playground/
    Playground.tsx
    ChartOutput.tsx
    Playground.module.css
  ```
* **Extract Hooks:** Put reusable feature state into `web/lib/domain/use*.ts` and generic utility hooks into `web/lib/use*.ts`.
* **Static export:** The site builds with `output: "export"`. No API routes, server actions or other server-only features.

---

## 3. CSS Design Tokens & Typography

* **Central Tokens:** Define all visual values as custom properties in `:root` of `web/app/globals.css`. Fonts load via `next/font/local` in `web/app/layout.tsx` (exposed as `--font-futura`).
* **Zero Hardcoded Values:** Never use raw hex colors, pixel sizes, margins, or padding outside the token definitions. Reference tokens via `var(--token-name)`.
* **Text Opacity Rule:** Never use solid hex greys for text. Use alpha transparent black/white (e.g. `rgba(0, 0, 0, 0.87)`, `rgba(0, 0, 0, 0.5)`).
* **Role-Based Typography:** Name utility classes after UI roles (e.g. `.shirin-pane-title`, `.shirin-hint`), not abstract scales. Compose them in CSS modules (`composes: shirin-hint from global;`).

---

## 4. Error Handling & Fail Hard Policy

* **Fail Hard:** Never swallow errors or return dummy fallbacks (`[]`, `{}`, `None`). Raise or throw explicitly with a message naming the bad value (e.g. `raise KeyError(f"Palette missing keys: {missing}")`).
* **Strict Environment Variables:** Never use inline fallbacks (`process.env.KEY || 'default'`, `os.getenv("KEY", "default")`). Fail immediately if a required variable is missing.
* **Python errors in the playground:** Surface the full Python traceback in the output pane; never hide it.
* **Fallbacks Exception:** Implement fallback logic only when explicitly requested by user.

---

## 5. UI Loading States

* **Shimmer Skeletons:** While Pyodide loads or code runs, use content-shaped skeleton placeholders instead of generic spinners.
* **Animation:** Use a smooth ~2s sweep animation. Respect `prefers-reduced-motion`.

---

## 6. Comments Policy

* **Minimal Comments:** Never explain what code does. Use clear naming instead.
* **Why, Not What:** Reserve comments exclusively for non-obvious rationale, workarounds, or external API constraints.
