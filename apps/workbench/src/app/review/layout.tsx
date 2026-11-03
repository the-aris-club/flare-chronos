import { getTranslations } from 'next-intl/server';
import { ReviewShell } from '@/components/review/review-shell';

export async function generateMetadata() {
  const t = await getTranslations('Meta');
  return { title: t('reviewTitle') };
}

export default function ReviewLayout({ children }: { children: React.ReactNode }) {
  return <ReviewShell>{children}</ReviewShell>;
}
