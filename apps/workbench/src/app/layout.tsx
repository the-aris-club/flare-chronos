import type { Metadata } from 'next';
import Script from 'next/script';
import { IBM_Plex_Mono, IBM_Plex_Sans } from 'next/font/google';
import { cookies } from 'next/headers';
import { NextIntlClientProvider } from 'next-intl';
import { getLocale, getMessages, getTranslations } from 'next-intl/server';
import { GlobeMorph } from '@/components/globe/globe-morph';
import { QueryProvider } from '@/components/query-provider';
import { LoadingProvider } from '@/components/ui/loading-provider';
import { ServiceProvider } from '@/components/service/service-provider';
import { ThemeProvider } from '@/components/ui/theme-provider';
import { DEFAULT_THEME, isTheme, THEME_COOKIE } from '@/lib/theme';
import './globals.css';

const sans = IBM_Plex_Sans({
  subsets: ['latin', 'vietnamese'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-plex-sans',
  display: 'swap',
});

const mono = IBM_Plex_Mono({
  subsets: ['latin', 'vietnamese'],
  weight: ['400', '500', '600'],
  variable: '--font-plex-mono',
  display: 'swap',
});

const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? 'https://flare-chronos.resonance.io.vn';

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('Meta');
  const title = t('title');
  const description = t('description');

  return {
    metadataBase: new URL(SITE_URL),
    title,
    description,
    openGraph: {
      type: 'website',
      siteName: 'FlareChronos',
      title: t('homeTitle'),
      description,
      url: '/',
      images: [
        {
          url: '/og.png',
          width: 1200,
          height: 630,
          alt: t('homeTitle'),
        },
      ],
    },
    twitter: {
      card: 'summary_large_image',
      title: t('homeTitle'),
      description,
      images: ['/og.png'],
    },
  };
}

export default async function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  const [locale, messages, store] = await Promise.all([getLocale(), getMessages(), cookies()]);

  const candidate = store.get(THEME_COOKIE)?.value;
  const theme = isTheme(candidate) ? candidate : DEFAULT_THEME;

  return (
    <html lang={locale} data-theme={theme} suppressHydrationWarning>
      <body className={`${sans.variable} ${mono.variable} bg-canvas text-ink`}>
        <Script id="theme-cookie-sync" strategy="beforeInteractive">
          {`(function(){try{var m=document.cookie.match(/(?:^|; )fc-theme=([^;]+)/);var v=m?decodeURIComponent(m[1]):null;if(v==='dark'||v==='light')localStorage.setItem('fc-theme',v);}catch(e){}})();`}
        </Script>
        <NextIntlClientProvider locale={locale} messages={messages}>
          <ThemeProvider initialTheme={theme}>
            <ServiceProvider>
              <QueryProvider>
                <LoadingProvider>
                  {children}
                  <GlobeMorph />
                </LoadingProvider>
              </QueryProvider>
            </ServiceProvider>
          </ThemeProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
