'use client';

import { useTranslations } from 'next-intl';
import { ConnectPanel } from '@/components/workbench/service-panel';
import { useService } from '@/components/service/service-provider';

/** Review reads the service, and the token lives in memory only, so a reload asks again. */
export function ReviewGate({ children }: { children: React.ReactNode }) {
  const t = useTranslations('Review');
  const service = useService();

  if (service.connection === 'connected') return <>{children}</>;

  return (
    <div className="mx-auto flex w-full max-w-lg flex-col gap-3 px-3 py-10">
      <p className="text-body text-ink-muted">{t('connectFirst')}</p>
      <ConnectPanel />
    </div>
  );
}
