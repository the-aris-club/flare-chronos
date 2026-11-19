import path from 'node:path';
import type { NextConfig } from 'next';
import createNextIntlPlugin from 'next-intl/plugin';

const nextConfig: NextConfig = {
  output: 'standalone',
  reactCompiler: true,
  devIndicators: false,
  // The loaders read these two artifacts with `node:fs` at request time.
  // Trace them so the Vercel server function ships them in its bundle.
  // ponytail: copies of `data/processed` live in the app; refresh both when the
  // artifacts change. Upgrade when Vercel can include files outside the app root.
  outputFileTracingIncludes: {
    '/*': ['data/processed/burning_calendar.json', 'data/processed/empirical_results.json'],
  },
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'Content-Security-Policy', value: "frame-ancestors 'self'" },
        ],
      },
    ];
  },
  turbopack: {
    root: path.resolve(),
    rules: {
      '*.css': {
        loaders: ['@tailwindcss/turbopack'],
        as: '*.css',
      },
    },
  },
};

const withNextIntl = createNextIntlPlugin('./src/i18n/request.ts');

export default withNextIntl(nextConfig);
