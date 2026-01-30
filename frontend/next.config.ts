import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow connecting to backend on different port in development
  async rewrites() {
    return [];
  },
};

export default nextConfig;
