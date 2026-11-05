import HomeGallery from "@/components/domain/HomeGallery";
import { getCategories } from "@/app/categories";
import { getHomeCharts } from "@/app/homeCharts";

export default function Home() {
  return <HomeGallery categories={getCategories()} charts={getHomeCharts()} />;
}
