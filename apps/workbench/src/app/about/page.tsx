import { getTranslations } from 'next-intl/server';
import Link from 'next/link';

export async function generateMetadata() {
  const t = await getTranslations('About');
  return {
    title: t('title'),
    description: t('subtitle'),
    alternates: { canonical: '/about' },
    openGraph: {
      type: 'article',
      title: t('title'),
      description: t('subtitle'),
      url: '/about',
    },
  };
}

export default async function AboutPage() {
  const t = await getTranslations('About');
  const method = t.raw('method') as string[];
  const figures = t.raw('figures') as { title: string; caption: string }[];
  const sources = t.raw('sources') as string[];

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'AboutPage',
    name: t('title'),
    description: t('subtitle'),
    url: '/about',
    isPartOf: { '@type': 'WebSite', name: 'Flare Chronos', url: '/' },
  };

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <script type="application/ld+json">{JSON.stringify(jsonLd)}</script>
      <h1 className="text-3xl font-semibold">{t('title')}</h1>
      <p className="text-muted mt-2 text-lg">{t('subtitle')}</p>
      <p className="mt-6 leading-relaxed">{t('intro')}</p>

      <h2 className="mt-10 text-2xl font-semibold">{t('problemTitle')}</h2>
      <p className="mt-4 leading-relaxed">{t('problem')}</p>

      <h2 className="mt-10 text-2xl font-semibold">{t('methodTitle')}</h2>
      <ul className="mt-4 list-disc space-y-2 pl-6">
        {method.map((m) => (
          <li key={m} className="leading-relaxed">
            {m}
          </li>
        ))}
      </ul>

      <h2 className="mt-10 text-2xl font-semibold">{t('evidenceTitle')}</h2>
      <p className="mt-4 leading-relaxed">{t('evidenceIntro')}</p>
      <ul className="mt-4 space-y-4">
        {figures.map((f) => (
          <li key={f.title}>
            <strong>{f.title}</strong>
            <p className="text-muted">{f.caption}</p>
          </li>
        ))}
      </ul>

      <h2 className="mt-10 text-2xl font-semibold">{t('sourcesTitle')}</h2>
      <ul className="mt-4 list-disc space-y-2 pl-6">
        {sources.map((s) => (
          <li key={s} className="leading-relaxed">
            {s}
          </li>
        ))}
      </ul>

      <h2 className="mt-10 text-2xl font-semibold">{t('creditsTitle')}</h2>
      <p className="mt-4 leading-relaxed">{t('credits')}</p>

      <h2 className="mt-10 text-2xl font-semibold">{t('licenseTitle')}</h2>
      <p className="mt-4 leading-relaxed">{t('license')}</p>

      <div className="mt-10">
        <Link href="/" className="underline">
          {t('cta')}
        </Link>
      </div>
    </main>
  );
}
