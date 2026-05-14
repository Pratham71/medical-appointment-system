/** @type {import('next').NextConfig} */
const backendApiUrl = process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000";

const nextConfig = {
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${backendApiUrl.replace(/\/$/, "")}/:path*`,
      },
    ];
  },
};

export default nextConfig;
