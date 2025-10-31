import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Note: Frontend deploys to Vercel (not Docker)
  // Do NOT use 'output: "standalone"' - Vercel handles build automatically

  experimental: {
    ppr: true,
  },

  images: {
    remotePatterns: [
      {
        hostname: "avatar.vercel.sh",
      },
    ],
  },
};

export default nextConfig;
