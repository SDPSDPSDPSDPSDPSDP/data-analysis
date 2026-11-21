import type { Metadata } from "next";
import Nav from "@/components/domain/Nav";
import Playground from "@/components/domain/Playground";
import { sectionId } from "@/lib/sections";
import { getCategories, getSetup } from "@/app/categories";

export function generateStaticParams() {
  return getCategories().map((category) => ({ category: sectionId(category.title) }));
}

type Props = { params: Promise<{ category: string }> };

async function findCategory(params: Props["params"]) {
  const { category: slug } = await params;
  const categories = getCategories();
  const category = categories.find((c) => sectionId(c.title) === slug);
  if (!category) throw new Error(`Unknown category "${slug}"`);
  return { slug, categories, category };
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { category } = await findCategory(params);
  const sections = category.sections.map((section) => section.title.toLowerCase()).join(", ");
  return { title: category.title, description: `Runnable shirin examples: ${sections}.` };
}

export default async function CategoryPage({ params }: Props) {
  const { slug, categories, category } = await findCategory(params);
  return (
    <>
      <Nav categories={categories} />
      <Playground
        title={category.title}
        setup={getSetup()}
        categories={[category]}
        showSetup={slug !== "tools"}
        expanded
      />
    </>
  );
}
