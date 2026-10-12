import HomeGallery from "@/components/domain/HomeGallery";
import { getCategories, getHomeCharts } from "@/app/categories";

export default function Home() {
  return <HomeGallery categories={getCategories()} charts={getHomeCharts()} />;
}
