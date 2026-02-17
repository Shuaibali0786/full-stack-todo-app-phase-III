const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Fix: tell Next.js the tracing root is this directory (frontend/)
  // Prevents multiple-lockfile confusion on Vercel
  outputFileTracingRoot: path.join(__dirname),
};

module.exports = nextConfig;
