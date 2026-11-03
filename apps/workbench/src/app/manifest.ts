import type { MetadataRoute } from 'next';

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: 'Flare Chronos — Workbench',
    short_name: 'Flare Chronos',
    description: 'Cross-sensor harmonization of satellite active-fire records (MODIS + VIIRS) for the Mekong and Amazon regions, 2000–2026.',
    start_url: '/',
    display: 'standalone',
    background_color: '#0b0f14',
    theme_color: '#0b0f14',
    icons: [
      { src: '/icon.png', sizes: '512x512', type: 'image/png' },
      { src: '/logo.png', sizes: '512x512', type: 'image/png' },
    ],
  };
}
