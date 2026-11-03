'use client';

import { useCallback, useMemo, useState, type ChangeEvent, type MouseEvent } from 'react';
import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { useService } from '@/components/service/service-provider';
import { Icon, ICON } from '@/components/ui/icon';
import type { ReviewStatus } from '@/lib/review/api';
import { useLabels } from './use-labels';
import { StatusChip, utcTime } from './review-bits';

const TABS: ReviewStatus[] = ['needs', 'published', 'withheld', 'failed'];
const ICONS = {
  needs: ICON.dot,
  published: ICON.check,
  withheld: ICON.close,
  failed: ICON.alert,
} as const;

export function ReviewQueue() {
  const t = useTranslations('Review');
  const labels = useLabels();
  const service = useService();
  const [tab, setTab] = useState<ReviewStatus>('needs');
  const [query, setQuery] = useState('');

  const handleTabClick = useCallback((event: MouseEvent<HTMLButtonElement>) => {
    const value = event.currentTarget.dataset.value as ReviewStatus;
    setTab(value);
  }, []);

  const handleQueryChange = useCallback((event: ChangeEvent<HTMLInputElement>) => {
    setQuery(event.target.value);
  }, []);

  const counts = useMemo(() => {
    const next: Record<ReviewStatus, number> = { needs: 0, published: 0, withheld: 0, failed: 0 };
    for (const row of service.rows) next[row.status] += 1;
    return next;
  }, [service.rows]);

  const rows = useMemo(() => {
    const search = query.trim().toLowerCase();
    return service.rows.filter(
      (row) =>
        row.status === tab &&
        (!search || [row.id, row.useCase, row.owner].join(' ').toLowerCase().includes(search)),
    );
  }, [service.rows, tab, query]);

  return (
    <div className="tablet:px-5 tablet:py-6 mx-auto flex w-full max-w-400 flex-col gap-4 px-3 py-4">
      <header className="flex flex-col gap-1">
        <h1 className="text-display font-semibold tracking-tight">{t('queue')}</h1>
        <p className="text-body text-ink-muted max-w-3xl">{t('queueSub')}</p>
      </header>

      {service.rowsFailure && (
        <p role="alert" className="text-meta text-bad">
          {t('queueFailed')}
        </p>
      )}

      <div className="border-line flex gap-1 border-b">
        {TABS.map((value) => (
          <button
            key={value}
            type="button"
            onClick={handleTabClick}
            data-value={value}
            aria-pressed={tab === value}
            className={`text-body -mb-px inline-flex items-center gap-1.5 border-b-2 px-2.5 py-2 font-medium ${
              tab === value
                ? 'border-cyan text-ink'
                : 'text-ink-muted hover:text-ink border-transparent'
            }`}
          >
            <Icon icon={ICONS[value]} size="xs" />
            {t(value)}
            <span className="text-label text-ink-subtle font-mono">{counts[value]}</span>
          </button>
        ))}
      </div>

      <label className="relative max-w-md">
        <span className="sr-only">{t('search')}</span>
        <Icon
          icon={ICON.search}
          size="sm"
          className="text-ink-subtle pointer-events-none absolute top-2.5 left-2.5"
        />
        <input
          type="search"
          id="review-search"
          name="review-search"
          value={query}
          onChange={handleQueryChange}
          placeholder={t('search')}
          className="border-line-strong bg-raised text-body text-ink placeholder:text-ink-subtle h-9 w-full rounded-md border pr-2.5 pl-8"
        />
      </label>

      {rows.length === 0 ? (
        <div className="border-line text-meta text-ink-muted rounded-lg border border-dashed px-4 py-10 text-center">
          {query ? t('noMatch') : t('emptyQueue')}
        </div>
      ) : (
        <div className="border-line overflow-x-auto rounded-lg border">
          <table className="w-full min-w-160 border-collapse text-left">
            <thead>
              <tr className="bg-raised">
                {[t('run'), t('useCase'), t('status'), t('owner'), t('updated')].map((label) => (
                  <th
                    key={label}
                    scope="col"
                    className="text-label text-ink-muted border-line border-b px-2.5 py-2 font-mono font-medium whitespace-nowrap uppercase"
                  >
                    {label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-line hover:bg-raised border-b last:border-0">
                  <td className="px-2.5 py-2.5 align-top">
                    <Link
                      href={`/review/runs/${row.id}`}
                      className="text-body text-ink font-mono font-semibold underline-offset-2 hover:underline"
                    >
                      {row.id}
                    </Link>
                  </td>
                  <td className="px-2.5 py-2.5 align-top">
                    <span className="text-meta font-mono">{row.useCase}</span>
                    <span className="text-meta text-ink-muted block">
                      {labels.caseLabel(row.useCase)}
                    </span>
                  </td>
                  <td className="px-2.5 py-2.5 align-top">
                    <StatusChip status={row.status} />
                  </td>
                  <td className="text-meta px-2.5 py-2.5 align-top">{row.owner}</td>
                  <td className="text-meta text-ink-subtle px-2.5 py-2.5 align-top font-mono whitespace-nowrap">
                    {utcTime(row.updatedAt)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="text-meta text-ink-subtle">{t('noBulk')}</p>
    </div>
  );
}
