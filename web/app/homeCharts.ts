// Relative with extension: scripts/build-previews.mjs imports this file with plain Node, which knows no "@/" alias.
import { exampleSetup, withDarkMode } from "../lib/exampleSetup.ts";
import { getCategories, getGlobalSetup } from "./categories.ts";
import { previewCodes, previewPath } from "./exampleFiles.ts";

const TITLE_LINE = /^[ \t]*title=(.*),[ \t]*\r?\n/m;

// Home gallery shows the title as text above the chart, so the preview is drawn without it.
function splitTitle(code: string) {
  const match = code.match(TITLE_LINE);
  if (!match) throw new Error(`Home gallery example has no single-line title=:\n${code}`);
  const [title, subtitle = null] = [...match[1].matchAll(/'([^']*)'|"([^"]*)"/g)].map((m) => m[1] ?? m[2]);
  if (title === undefined) throw new Error(`Home gallery title is not a string or list of strings: ${match[1]}`);
  return { title, subtitle, previewCode: code.replace(TITLE_LINE, "") };
}

// Home gallery charts. Sections without a data format are tools, not charts.
// cardPreview is the gallery image without title, preview the full chart for the modal. dark* are the dark_mode=True versions.
export function getHomeCharts() {
  const globalSetup = getGlobalSetup();
  return getCategories().flatMap((category) =>
    category.sections
      .filter((section) => section.dataFormats.length > 0)
      .flatMap((section) =>
        section.homeExamples.map((example) => {
          const setup = exampleSetup(globalSetup, section.setup, example);
          const { title, subtitle, previewCode } = splitTitle(example.code);
          const cardCode = `${setup}\n${previewCode}`;
          if (!example.preview || !example.darkPreview) throw new Error(`Home gallery example has no preview:\n${example.code}`);
          return {
            setup,
            code: example.code,
            title,
            subtitle,
            preview: example.preview,
            darkPreview: example.darkPreview,
            cardPreview: previewPath(cardCode),
            darkCardPreview: previewPath(withDarkMode(cardCode, true)),
            section: section.title,
            category: category.title,
          };
        }),
      ),
  );
}

// Every prerendered SVG with the code that draws it. previewPath registers each path as a side effect,
// so building the home charts (which builds every category) is what fills previewCodes.
export function getPreviews() {
  getHomeCharts();
  return [...previewCodes].map(([path, code]) => ({ path, code }));
}
