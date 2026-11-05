import Nav from "@/components/domain/Nav";
import Playground from "@/components/domain/Playground";
import type { Metadata } from "next";
import { getCategories, getSetup } from "@/app/categories";

export const metadata: Metadata = {
  title: "All examples",
  description: "Every shirin chart type with runnable Python examples.",
};

export default function All() {
  const categories = getCategories();
  return (
    <>
      <Nav categories={categories} />
      <Playground title="All examples" setup={getSetup()} categories={categories} showSetup expanded={false} />
    </>
  );
}
