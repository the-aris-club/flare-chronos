import type { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  const base = process.env.NEXT_PUBLIC_SITE_URL ?? 'https://flare-chronos.resonance.io.vn';
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/workbench/', '/review/', '/api/'],
      },
    ],
    sitemap: `${base}/sitemap.xml`,
    host: base,
  };
}
