import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  // Keeps the dev badge out of local portfolio stills.
  devIndicators: false,
};

export default nextConfig;
