import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  // No "js": keeps Next from treating Vercel's middleware.js as Next middleware, which
  // output: "export" rejects.
  pageExtensions: ["tsx", "ts"],
  // Keeps the dev badge out of local portfolio stills.
  devIndicators: false,
  experimental: {
    agentUpgrade: "security",
  },
};

export default nextConfig;
