'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import { useTranslations } from 'next-intl';
import { useService } from '@/components/service/service-provider';
import { Icon, ICON } from '@/components/ui/icon';
import { parseAudit, type AuditRow } from '@/lib/review/api';
import { utcTime } from './review-bits';
import { FilterSelect } from './review-select';
import { useLabels } from './use-labels';

function csvCell(value: string): string {
  return `"${value.replaceAll('"', '""')}"`;
}

type Row = AuditRow & { useCase: string };

const DECISION_OPTIONS = ['approve', 'reject'];

export function ReviewAudit() {
  const t = useTranslations('Review');
  const labels = useLabels();
  const service = useService();
  const [all, setAll] = useState<Row[]>([]);
  const [failed, setFailed] = useState(false);
  const [reviewer, setReviewer] = useState('all');
  const [decision, setDecision] = useState('all');
  const [date, setDate] = useState('all');
  const [useCase, setUseCase] = useState('all');
  const { get, rows: runs } = service;

  useEffect(() => {
    let live = true;
    const decided = runs.filter((run) => run.status !== 'needs');
    Promise.all(
      decided.map(async (run) => {
        const result = await get(`/api/v1/review/runs/${run.id}/audit`);
        if (!result.ok) throw new Error(result.reason);
        return parseAudit(result.data).map((row) => ({ ...row, useCase: run.useCase }));
      }),
    )
      .then((groups) => {
        if (!live) return;
        setAll(groups.flat().sort((a, b) => b.decidedAt.localeCompare(a.decidedAt)));
        setFailed(false);
      })
      .catch(() => live && setFailed(true));
    return () => {
      live = false;
    };
  }, [get, runs]);

  const reviewers = useMemo(() => [...new Set(all.map((row) => row.principal))], [all]);
  const dates = useMemo(
    () => [...new Set(all.map((row) => row.decidedAt.slice(0, 10)))].sort().reverse(),
    [all],
  );
  const cases = useMemo(() => [...new Set(all.map((row) => row.useCase))], [all]);
  const decisionLabels = useMemo(() => ({ approve: t('approved'), reject: t('rejected') }), [t]);

  const rows = useMemo(
    () =>
      all.filter((row) => {
        if (reviewer !== 'all' && row.principal !== reviewer) return false;
        if (decision !== 'all' && (row.approved ? 'approve' : 'reject') !== decision) return false;
        if (date !== 'all' && !row.decidedAt.startsWith(date)) return false;
        if (useCase !== 'all' && row.useCase !== useCase) return false;
        return true;
      }),
    [all, reviewer, decision, date, useCase],
  );

  const download = useCallback((name: string, content: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = name;
    anchor.click();
    URL.revokeObjectURL(url);
  }, []);

  const exportCsv = useCallback(() => {
    const header = ['utc_time', 'run', 'reviewer', 'decision', 'reason_code', 'note', 'audit_id'];
    const body = rows.map((row) =>
      [
        row.decidedAt,
        row.runId,
        row.principal,
        row.approved ? 'approve' : 'reject',
        row.reasonCode,
        row.reason,
        row.id,
      ]
        .map(csvCell)
        .join(','),
    );
    download('flare-chronos-audit.csv', [header.join(','), ...body].join('\n'), 'text/csv');
  }, [rows, download]);

  const exportJson = useCallback(() => {
    const data = rows.map((row) => ({
      utc_time: row.decidedAt,
      run: row.runId,
      reviewer: row.principal,
      decision: row.approved ? 'approve' : 'reject',
      reason_code: row.reasonCode,
      note: row.reason,
      audit_id: row.id,
    }));
    download('flare-chronos-audit.json', JSON.stringify(data, null, 2), 'application/json');
  }, [rows, download]);

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
            <Icon icon={ICON.download} size="sm" />
            {t('exportCsv')}
          </button>
          <button
            type="button"
            onClick={exportJson}
            className="border-line-strong text-meta hover:bg-chip inline-flex h-8 items-center gap-1.5 rounded-md border px-2.5 font-medium"
          >
            <Icon icon={ICON.download} size="sm" />
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
          options={DECISION_OPTIONS}
          labels={decisionLabels}
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

      {failed && (
        <p role="alert" className="text-meta text-bad">
          {t('queueFailed')}
        </p>
      )}

      {rows.length === 0 ? (
        <div className="border-line text-meta text-ink-muted rounded-lg border border-dashed px-4 py-10 text-center">
          {t('auditNone')}
        </div>
      ) : (
        <div className="border-line overflow-x-auto rounded-lg border">
          <table className="w-full min-w-180 border-collapse text-left">
            <thead>
              <tr className="bg-raised">
                {[
                  t('time'),
                  t('run'),
                  t('reviewer'),
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
                <tr key={row.id} className="border-line border-b last:border-0">
                  <td className="text-meta px-2.5 py-2 font-mono">
                    {row.decidedAt.slice(0, 10)} {utcTime(row.decidedAt)}
                  </td>
                  <td className="text-meta px-2.5 py-2 font-mono">{row.runId}</td>
                  <td className="text-meta px-2.5 py-2">{row.principal}</td>
                  <td className="px-2.5 py-2">
                    <span
                      className={`text-label inline-flex items-center gap-1 rounded-sm border px-1.5 font-mono ${
                        row.approved ? 'border-ok text-ok' : 'border-bad text-bad'
                      }`}
                    >
                      <Icon icon={row.approved ? ICON.check : ICON.close} size="xs" />
                      {row.approved ? t('approved') : t('rejected')}
                    </span>
                  </td>
                  <td className="text-meta px-2.5 py-2">{labels.reason(row.reasonCode)}</td>
                  <td className="text-meta text-ink-muted px-2.5 py-2">{row.reason || '—'}</td>
                  <td className="text-meta px-2.5 py-2 font-mono">{row.id}</td>
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
