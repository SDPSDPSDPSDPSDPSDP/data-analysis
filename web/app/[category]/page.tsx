import Nav from "@/components/domain/Nav";
import Playground from "@/components/domain/Playground";
import { sectionId } from "@/components/domain/PlotSection";
import { getCategories, getSetup } from "@/app/categories";

export function generateStaticParams() {
  return getCategories().map((category) => ({ category: sectionId(category.title) }));
}

export default async function CategoryPage({ params }: { params: Promise<{ category: string }> }) {
  const { category: slug } = await params;
  const categories = getCategories();
  const category = categories.find((c) => sectionId(c.title) === slug);
  if (!category) throw new Error(`Unknown category "${slug}"`);
  return (
    <>
      <Nav categories={categories} />
      <Playground setup={getSetup()} categories={[category]} expanded />
    </>
  );
}
