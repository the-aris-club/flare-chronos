'use client';

import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { BrandMark } from '@/components/ui/brand-mark';
import { Icon, ICON } from '@/components/ui/icon';
import { useService } from '@/components/service/service-provider';
import { LocaleToggle } from '@/components/ui/locale-toggle';
import { ThemeToggle } from '@/components/ui/theme-toggle';

export function LandingHeader({ years }: { years: number }) {
  const t = useTranslations('Globe');
  const header = useTranslations('Header');
  const service = useService();
  const connected = service.connection === 'connected';

  return (
    <header className="pointer-events-none fixed inset-x-0 top-0 z-30 flex items-center gap-2 px-4 py-3 xl:px-14 xl:py-4">
      <div className="pointer-events-auto">
        <BrandMark large subtitle={t('subtitle', { years })} />
      </div>

      <nav className="pointer-events-auto ml-4 hidden items-center gap-3 xl:flex">
        <Link href="/about" className="text-meta text-ink-muted hover:text-ink">
          {header('about')}
        </Link>
        <Link href="/faq" className="text-meta text-ink-muted hover:text-ink">
          {header('faq')}
        </Link>
      </nav>

      <div className="pointer-events-auto ml-auto flex items-center gap-2">
        <span className="border-line bg-panel/70 text-meta text-ink-muted tablet:inline-flex hidden h-8 items-center gap-1.5 rounded-md border px-2.5 backdrop-blur-sm">
          <Icon icon={ICON.service} size="sm" className={connected ? 'text-ok' : 'text-amber'} />
          {connected ? header('connected') : header('notConnected')}
        </span>
        <LocaleToggle />
        <ThemeToggle />
      </div>
    </header>
  );
}
