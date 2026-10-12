import Link from "next/link";
import Nav from "@/components/domain/Nav";
import { sectionId } from "@/components/domain/PlotSection";
import SectionIcon from "@/components/domain/SectionIcon";
import { getCategories } from "@/app/categories";

export default function Home() {
  const categories = getCategories();
  const cards = [
    ...categories.map((category) => ({
      title: category.title,
      href: `/${sectionId(category.title)}`,
      items: category.sections.map((section) => section.title),
    })),
    { title: "All", href: "/all", items: ["Every example on one page"] },
  ];
  return (
    <>
      <Nav categories={categories} />
      <main className="page">
        <div className="home-cards">
          {cards.map((card) => (
            <Link key={card.title} href={card.href} className="home-card">
              <span className="home-card-icon">
                <SectionIcon title={card.title} />
              </span>
              <h3>{card.title}</h3>
              <p>{card.items.join(", ")}</p>
            </Link>
          ))}
        </div>
      </main>
    </>
  );
}
