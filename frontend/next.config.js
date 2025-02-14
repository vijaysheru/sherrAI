/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export", // ✅ Fix for Next.js 15+
  images: {
    unoptimized: true, // ✅ Fixes image issues in static export
  },
};

module.exports = nextConfig;
