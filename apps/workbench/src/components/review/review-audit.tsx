'use client';

import { useMemo, useState } from 'react';
import { useLocale, useTranslations } from 'next-intl';
import { useReviewStore } from '@/components/review/review-store';
import { AmIcon, ICON } from '@/components/ui/icon';
import { reasonLabel, RoleText, utcTime } from './review-bits';
import { FilterSelect } from './review-select';

// Decision and audit rows persist through /api/review/decisions.

function csvCell(value: string): string {
  return `"${value.replaceAll('"', '""')}"`;
}

export function ReviewAudit() {
  const t = useTranslations('Review');
  const locale = useLocale();
  const store = useReviewStore();
  const [reviewer, setReviewer] = useState('all');
  const [decision, setDecision] = useState('all');
  const [date, setDate] = useState('all');
  const [useCase, setUseCase] = useState('all');

  const reviewers = [...new Set(store.audit.map((row) => row.reviewer))];
  const dates = [...new Set(store.audit.map((row) => row.at.slice(0, 10)))].sort().reverse();
  const cases = [...new Set(store.audit.map((row) => row.useCase))];

  const rows = useMemo(
    () =>
      store.audit.filter((row) => {
        if (reviewer !== 'all' && row.reviewer !== reviewer) return false;
        if (decision !== 'all' && row.kind !== decision) return false;
        if (date !== 'all' && !row.at.startsWith(date)) return false;
        if (useCase !== 'all' && row.useCase !== useCase) return false;
        return true;
      }),
    [store.audit, reviewer, decision, date, useCase],
  );

  function download(name: string, content: string, type: string) {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = name;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function exportCsv() {
    const header = [
      'utc_time',
      'run',
      'reviewer',
      'role',
      'decision',
      'reason',
      'note',
      'audit_id',
    ];
    const body = rows.map((row) =>
      [
        row.at,
        row.runId,
        row.reviewer,
        row.role,
        row.kind,
        reasonLabel(row.reason, locale),
        row.note,
        row.audit,
      ]
        .map(csvCell)
        .join(','),
    );
    download('flare-chronos-audit.csv', [header.join(','), ...body].join('\n'), 'text/csv');
  }

  function exportJson() {
    const data = rows.map((row) => ({
      utc_time: row.at,
      run: row.runId,
      reviewer: row.reviewer,
      role: row.role,
      decision: row.kind,
      reason: row.reason,
      note: row.note,
      audit_id: row.audit,
    }));
    download('flare-chronos-audit.json', JSON.stringify(data, null, 2), 'application/json');
  }

  return (
    <div className="tablet:px-5 tablet:py-6 mx-auto flex w-full max-w-400 flex-col gap-4 px-3 py-4">
      <header className="flex flex-wrap items-end gap-2">
        <div className="flex flex-col gap-1">
          <h1 className="text-display font-semibold tracking-tight">{t('audit')}</h1>
          <p className="text-body text-ink-muted">{t('auditSub')}</p>
        </div>
        <div className="ml-auto flex gap-2">
          <button
            type="button"
            onClick={exportCsv}
            className="border-line-strong text-meta hover:bg-chip inline-flex h-8 items-center gap-1.5 rounded-md border px-2.5 font-medium"
          >
            <AmIcon icon={ICON.download} size="sm" />
            {t('exportCsv')}
          </button>
          <button
            type="button"
            onClick={exportJson}
            className="border-line-strong text-meta hover:bg-chip inline-flex h-8 items-center gap-1.5 rounded-md border px-2.5 font-medium"
          >
            <AmIcon icon={ICON.download} size="sm" />
            {t('exportJson')}
          </button>
        </div>
      </header>

      <div className="flex flex-wrap gap-2">
        <FilterSelect
          label={t('reviewer')}
          value={reviewer}
          onChange={setReviewer}
          options={reviewers}
          all={t('all')}
        />
        <FilterSelect
          label={t('decision')}
          value={decision}
          onChange={setDecision}
          options={['approve', 'reject']}
          labels={{ approve: t('approved'), reject: t('rejected') }}
          all={t('all')}
        />
        <FilterSelect
          label={t('date')}
          value={date}
          onChange={setDate}
          options={dates}
          all={t('all')}
        />
        <FilterSelect
          label={t('useCase')}
          value={useCase}
          onChange={setUseCase}
          options={cases}
          all={t('all')}
        />
      </div>

      {rows.length === 0 ? (
        <div className="border-line text-meta text-ink-muted rounded-lg border border-dashed px-4 py-10 text-center">
          {t('auditNone')}
        </div>
      ) : (
        <div className="border-line overflow-x-auto rounded-lg border">
          <table className="w-full min-w-200 border-collapse text-left">
            <thead>
              <tr className="bg-raised">
                {[
                  t('time'),
                  t('run'),
                  t('reviewer'),
                  t('role'),
                  t('decision'),
                  t('reason'),
                  t('noteShort'),
                  t('auditId'),
                ].map((label) => (
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
                <tr key={row.audit} className="border-line border-b last:border-0">
                  <td className="text-meta px-2.5 py-2 font-mono">{utcTime(row.at)}</td>
                  <td className="text-meta px-2.5 py-2 font-mono">{row.runId}</td>
                  <td className="text-meta px-2.5 py-2">{row.reviewer}</td>
                  <td className="text-meta text-ink-muted px-2.5 py-2">
                    <RoleText role={row.role} />
                  </td>
                  <td className="px-2.5 py-2">
                    <span
                      className={`text-label inline-flex items-center gap-1 rounded-sm border px-1.5 font-mono ${
                        row.kind === 'approve' ? 'border-ok text-ok' : 'border-bad text-bad'
                      }`}
                    >
                      <AmIcon icon={row.kind === 'approve' ? ICON.check : ICON.close} size="xs" />
                      {row.kind === 'approve' ? t('approved') : t('rejected')}
                    </span>
                  </td>
                  <td className="text-meta px-2.5 py-2">{reasonLabel(row.reason, locale)}</td>
                  <td className="text-meta text-ink-muted px-2.5 py-2">{row.note || '—'}</td>
                  <td className="text-meta px-2.5 py-2 font-mono">{row.audit}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <p className="text-meta text-ink-subtle">{t('readOnly')}</p>
    </div>
  );
}
