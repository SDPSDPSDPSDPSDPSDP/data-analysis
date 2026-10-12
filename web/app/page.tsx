import Nav from "@/components/domain/Nav";
import ChartPreview from "@/components/domain/ChartPreview";
import { exampleSetup, sectionId } from "@/components/domain/PlotSection";
import { getCategories, getSetup } from "@/app/categories";

export default function Home() {
  const categories = getCategories();
  const globalSetup = getSetup().map((cell) => cell.code).join("\n\n");
  // The first example of each section is shown on its category page, so only the others.
  // Sections without a data format are tools, not charts.
  const charts = categories.flatMap((category) =>
    category.sections
      .filter((section) => section.dataFormats.length > 0)
      .flatMap((section) =>
        section.examples.slice(1).map((example) => ({
          code: `${exampleSetup(globalSetup, section.setup, example)}\n${example.code}`,
          href: `/${sectionId(category.title)}`,
        })),
      ),
  );
  return (
    <>
      <Nav categories={categories} />
      <main className="page">
        <div className="home-charts">
          {charts.map((chart, i) => (
            <ChartPreview key={i} {...chart} />
          ))}
        </div>
      </main>
    </>
  );
}
