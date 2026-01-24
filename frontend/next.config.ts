import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  // Speed up development
  typescript: {
    // Don't type-check during build in dev mode
    ignoreBuildErrors: false,
  },
  eslint: {
    // Don't run ESLint during build
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
