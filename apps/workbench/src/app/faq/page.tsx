import { getTranslations } from 'next-intl/server';

export async function generateMetadata() {
  const t = await getTranslations('Faq');
  return {
    title: t('title'),
    description: t('subtitle'),
    alternates: { canonical: '/faq' },
    openGraph: {
      type: 'website',
      title: t('title'),
      description: t('subtitle'),
      url: '/faq',
    },
  };
}

export default async function FaqPage() {
  const t = await getTranslations('Faq');
  const items = t.raw('items') as { q: string; a: string }[];

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: items.map((it) => ({
      '@type': 'Question',
      name: it.q,
      acceptedAnswer: { '@type': 'Answer', text: it.a },
    })),
  };

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <script type="application/ld+json">{JSON.stringify(jsonLd)}</script>
      <h1 className="text-3xl font-semibold">{t('title')}</h1>
      <p className="mt-2 text-lg text-muted">{t('subtitle')}</p>
      <div className="mt-8 space-y-6">
        {items.map((it) => (
          <section key={it.q}>
            <h2 className="text-xl font-semibold">{it.q}</h2>
            <p className="mt-2 leading-relaxed">{it.a}</p>
          </section>
        ))}
      </div>
    </main>
  );
}
