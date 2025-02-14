/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export", // ✅ Required for static export
  images: {
    unoptimized: true, // ✅ Fixes Next.js image issues on static hosting
  },
};

module.exports = nextConfig;
