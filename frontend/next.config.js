module.exports = {
  reactStrictMode: true,
  async rewrites() {
    if (!process.env.NEXT_PUBLIC_API_URL) {
      console.error("❌ NEXT_PUBLIC_API_URL is not set!");
      return [];
    }

    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL}/:path*`,
      },
    ];
  },
};
