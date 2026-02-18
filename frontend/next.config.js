const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Explicitly set tracing root to this directory (frontend/)
  outputFileTracingRoot: path.join(__dirname),

  // Explicitly configure webpack @/ alias so it works on Vercel
  // regardless of workspace root detection
  webpack: (config) => {
    config.resolve.alias['@'] = path.join(__dirname, 'src');
    return config;
  },
};

module.exports = nextConfig;
