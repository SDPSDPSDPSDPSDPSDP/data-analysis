import Nav from "@/components/domain/Nav";
import Playground from "@/components/domain/Playground";
import { getCategories, getSetup } from "@/app/categories";

export default function All() {
  const categories = getCategories();
  return (
    <>
      <Nav categories={categories} />
      <Playground setup={getSetup()} categories={categories} showSetup expanded={false} />
    </>
  );
}
