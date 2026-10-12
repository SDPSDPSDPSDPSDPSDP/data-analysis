import HomeGallery from "@/components/domain/HomeGallery";
import { exampleSetup } from "@/components/domain/PlotSection";
import { getCategories, getSetup } from "@/app/categories";

export default function Home() {
  const categories = getCategories();
  const globalSetup = getSetup()
    .map((cell) => cell.code)
    .join("\n\n");
  // The first example of each section is shown on its category page, so only the others.
  // Sections without a data format are tools, not charts.
  const charts = categories.flatMap((category) =>
    category.sections
      .filter((section) => section.dataFormats.length > 0)
      .flatMap((section) =>
        section.examples.slice(1).map((example) => ({
          setup: exampleSetup(globalSetup, section.setup, example),
          code: example.code,
          category: category.title,
        })),
      ),
  );
  return <HomeGallery categories={categories} charts={charts} />;
}
