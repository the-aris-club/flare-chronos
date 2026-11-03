'use client';

import { useCallback, useTransition, type MouseEvent } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { writeCookie } from '@/lib/browser';
import { LOCALE_COOKIE, locales, type Locale } from '@/i18n/config';

export function LocaleToggle() {
  const t = useTranslations('Header');
  const locale = useLocale();
  const router = useRouter();
  const [pending, startTransition] = useTransition();

  const choose = useCallback(
    (next: Locale) => {
      if (next === locale) return;

      writeCookie(LOCALE_COOKIE, next);
      startTransition(() => router.refresh());
    },
    [locale, router, startTransition],
  );

  const handleChoose = useCallback(
    (event: MouseEvent<HTMLButtonElement>) => {
      const next = event.currentTarget.dataset.locale as Locale | undefined;
      if (next) choose(next);
    },
    [choose],
  );

  return (
    <div
      role="group"
      aria-label={t('language')}
      className="border-line-strong inline-flex gap-0.5 rounded-md border p-0.5"
    >
      {locales.map((option) => (
        <button
          key={option}
          type="button"
          data-locale={option}
          onClick={handleChoose}
          aria-pressed={locale === option}
          aria-label={`${t(`lang.${option}`)} (${option.toUpperCase()})`}
          disabled={pending}
          className={`text-meta h-6 rounded-sm px-2 font-mono font-semibold uppercase transition-colors ${
            locale === option ? 'bg-seg text-ink' : 'text-ink-subtle hover:text-ink'
          }`}
        >
          {option}
        </button>
      ))}
    </div>
  );
}
