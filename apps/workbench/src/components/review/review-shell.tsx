'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { ReviewGate } from '@/components/review/review-gate';
import { useService } from '@/components/service/service-provider';
import { BrandMark } from '@/components/ui/brand-mark';
import { HeaderBar } from '@/components/ui/header-bar';
import { Icon, ICON } from '@/components/ui/icon';
import { LocaleToggle } from '@/components/ui/locale-toggle';
import { ThemeToggle } from '@/components/ui/theme-toggle';

export function ReviewShell({ children }: { children: React.ReactNode }) {
  const t = useTranslations('Review');
  const pathname = usePathname();
  const store = useService();
  const name = store.claims?.name ?? store.claims?.sub ?? '';
  const queueActive = pathname === '/review' || pathname.startsWith('/review/runs/');
  const auditActive = pathname.startsWith('/review/audit');

  return (
    <div className="bg-canvas flex min-h-dvh flex-col">
      <HeaderBar>
        <BrandMark />

        <Link
          href="/workbench/mekong"
          className="text-body text-ink-muted hover:text-ink tablet:inline-flex hidden items-center gap-1"
        >
          <Icon icon={ICON.back} size="sm" />
          {t('workbench')}
        </Link>

        <nav aria-label={t('review')} className="ml-2 flex h-full items-center gap-1">
          <Link
            href="/review"
            aria-current={queueActive ? 'page' : undefined}
            className={`text-body inline-flex h-full items-center gap-1.5 border-b-2 px-2 font-medium ${
              queueActive
                ? 'border-cyan text-ink'
                : 'text-ink-muted hover:text-ink border-transparent'
            }`}
          >
            {t('review')}
            {store.needsDecision > 0 && (
              <span className="bg-cyan text-canvas text-micro inline-flex h-4 min-w-4 items-center justify-center rounded-full px-1 font-mono font-semibold">
                {store.needsDecision}
              </span>
            )}
          </Link>
          <Link
            href="/review/audit"
            aria-current={auditActive ? 'page' : undefined}
            className={`text-body inline-flex h-full items-center gap-1.5 border-b-2 px-2 font-medium ${
              auditActive
                ? 'border-cyan text-ink'
                : 'text-ink-muted hover:text-ink border-transparent'
            }`}
          >
            {t('audit')}
          </Link>
        </nav>

        <div className="ml-auto flex items-center gap-2">
          {store.claims && (
            <span className="border-line text-micro text-ink-muted tablet:inline-flex hidden h-8 items-center gap-2 rounded-md border px-2">
              <span className="bg-seg text-ink text-micro inline-flex size-6 items-center justify-center rounded-full font-mono font-semibold">
                {name.slice(0, 2).toUpperCase()}
              </span>
              <span className="flex flex-col leading-tight">
                <span className="text-meta text-ink">{name}</span>
                <span className="text-micro text-ink-subtle font-mono uppercase">
                  {store.isApprover ? t('approver') : t('reviewer')}
                </span>
              </span>
            </span>
          )}
          <LocaleToggle />
          <ThemeToggle />
        </div>
      </HeaderBar>

      <main className="min-h-0 flex-1">
        <ReviewGate>{children}</ReviewGate>
      </main>
    </div>
  );
}
