import { getRequestConfig } from 'next-intl/server';
import { cookies } from 'next/headers';
import { defaultLocale, isLocale, LOCALE_COOKIE } from './config';

const messages = {
  en: () => import('./messages/en.json'),
  vi: () => import('./messages/vi.json'),
};

export default getRequestConfig(async () => {
  const store = await cookies();
  const candidate = store.get(LOCALE_COOKIE)?.value;
  const locale = isLocale(candidate) ? candidate : defaultLocale;

  return {
    locale,
    messages: (await messages[locale]()).default,
  };
});
