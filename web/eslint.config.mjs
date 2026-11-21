import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";

// Enforces the AGENTS.md hard rules that a linter can check.

// IntersectionObserver rootMargin and <img sizes> take px or %, never CSS variables.
const PX_ONLY_APIS = [
  ":not(JSXAttribute[name.name=/^(rootMargin|sizes)$/] *)",
  ":not(AssignmentPattern[left.name=/^(rootMargin|sizes)$/] > *)",
  ":not(Property[key.name=/^(rootMargin|sizes)$/] *)",
].join("");
export default defineConfig([
  ...nextVitals,
  globalIgnores([".next/**", "node_modules/**", "out/**", "public/**", "next-env.d.ts"]),
  {
    rules: {
      "max-lines": ["error", { max: 200, skipBlankLines: true, skipComments: true }],
      "max-depth": ["error", 3],
      complexity: ["error", 15],
      "no-nested-ternary": "error",
      // console.error / console.warn / console.info stay: server routes and audit events log with them.
      "no-console": ["error", { allow: ["error", "warn", "info"] }],
      "no-debugger": "error",
      // Accessibility basics on top of the few jsx-a11y rules next/core-web-vitals enables.
      "jsx-a11y/no-static-element-interactions": "error",
      "jsx-a11y/click-events-have-key-events": "error",
      "jsx-a11y/anchor-is-valid": "error",
      "jsx-a11y/html-has-lang": "error",
      "jsx-a11y/heading-has-content": "error",
      "no-restricted-syntax": [
        "error",
        {
          // Hardcoded defaults only: an optional override over real data (`env.X ?? fromDb`) is fine.
          selector:
            "LogicalExpression[left.object.object.name='process'][left.object.property.name='env'][right.type=/^(Literal|TemplateLiteral)$/]",
          message: "Fail hard: no env var fallback. Throw if missing.",
        },
        {
          // `||` only: `x ?? []` on an optional field reads "absent means none", not a masked error.
          selector: "LogicalExpression[operator='||'][right.type='ArrayExpression'][right.elements.length=0]",
          message: "Fail hard: no empty array fallback.",
        },
        {
          selector: "LogicalExpression[operator='||'][right.type='ObjectExpression'][right.properties.length=0]",
          message: "Fail hard: no empty object fallback.",
        },
        {
          // Double backslashes: in a JS string "\b" is a backspace and "\d" is "d".
          selector: `Literal[value=/#[0-9a-fA-F]{3,8}\\b|\\d+px\\b/]${PX_ONLY_APIS}`,
          message: "No raw colors or pixels. Use var(--token).",
        },
        {
          selector: `TemplateElement[value.raw=/#[0-9a-fA-F]{3,8}\\b|\\d+px\\b/]${PX_ONLY_APIS}`,
          message: "No raw colors or pixels. Use var(--token).",
        },
      ],
    },
  },
  {
    // Env only via typed getters in lib/env.ts. middleware.js is bundled alone by Vercel Routing Middleware
    // (not Next), so it reads its own env and checks it itself.
    ignores: ["lib/env.ts", "middleware.js"],
    rules: {
      "no-restricted-properties": [
        "error",
        {
          object: "process",
          property: "env",
          message: "Read env via the typed getters in lib/env.ts.",
        },
      ],
    },
  },
  {
    // Node CLI scripts (npm run <task>): stdout is their interface.
    files: ["scripts/**"],
    rules: { "no-console": "off" },
  },
  {
    files: ["components/ui/**"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["@/components/domain/*", "@/lib/data/*"],
              message: "ui/ is dumb primitives only. No data or domain imports.",
            },
            {
              group: ["@/lib/pyodide", "**/lib/pyodide"],
              message: "ui/ is dumb primitives only. No Pyodide calls.",
            },
          ],
        },
      ],
    },
  },
]);
