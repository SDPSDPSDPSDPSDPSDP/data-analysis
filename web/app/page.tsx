import HomeGallery from "@/components/domain/HomeGallery";
import { exampleSetup } from "@/components/domain/PlotSection";
import { getCategories, getSetup } from "@/app/categories";

export default function Home() {
  const categories = getCategories();
  const globalSetup = getSetup()
    .map((cell) => cell.code)
    .join("\n\n");
  // Sections without a data format are tools, not charts.
  const charts = categories.flatMap((category) =>
    category.sections
      .filter((section) => section.dataFormats.length > 0)
      .flatMap((section) =>
        section.homeExamples.map((example) => ({
          setup: exampleSetup(globalSetup, section.setup, example),
          code: example.code,
          section: section.title,
          category: category.title,
        })),
      ),
  );
  return <HomeGallery categories={categories} charts={charts} />;
}
