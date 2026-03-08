import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* ── Core ── */
  reactStrictMode: true,
  poweredByHeader: false, // Security: don't expose X-Powered-By

  /* ── Images ── */
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.supabase.co",
        pathname: "/storage/**",
      },
      {
        protocol: "https",
        hostname: "lh3.googleusercontent.com",
      },
      {
        protocol: "https",
        hostname: "avatars.githubusercontent.com",
      },
    ],
  },
};

export default nextConfig;
