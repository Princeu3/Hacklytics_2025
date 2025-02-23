/** @type {import('next').NextConfig} */
const nextConfig = {
  // Other existing config options...
  
  // Configure static file serving
  async headers() {
    return [
      {
        source: '/temp_uploads/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'no-store',
          },
        ],
      },
    ]
  },
  experimental: {
    serverActions: true,
  },
}

module.exports = nextConfig 