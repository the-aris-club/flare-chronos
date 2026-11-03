'use client';

import { useTranslations } from 'next-intl';

export default function WorkbenchError({ reset }: { reset: () => void }) {
  const t = useTranslations('Workbench');

  return (
    <main className="bg-canvas flex min-h-dvh items-center justify-center p-6">
      <div
        role="alert"
        className="border-line bg-panel flex w-full max-w-md flex-col gap-3 rounded-lg border p-5"
      >
        <h1 className="text-subhead font-semibold">{t('error')}</h1>
        <button
          type="button"
          onClick={reset}
          className="border-line-strong text-body text-ink hover:bg-chip self-start rounded-md border px-3 py-1.5 font-medium"
        >
          {t('retry')}
        </button>
      </div>
    </main>
  );
}
