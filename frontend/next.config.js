/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true, // Fixes image issues
  },
  experimental: {
    appDir: false, // Ensures compatibility with older Next.js projects
  },
};

module.exports = nextConfig;
