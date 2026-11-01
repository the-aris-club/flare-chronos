'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import { useLocale, useTranslations } from 'next-intl';
import { useReviewStore } from '@/components/review/review-store';
import { AmIcon, ICON } from '@/components/ui/icon';
import { PRINCIPAL, statusOf, type ReviewRun, type RunStatus } from '@/data/fixtures/review';
import { StatusChip, UrgencyChip, utcTime } from './review-bits';
import { FilterSelect } from './review-select';

const TABS: RunStatus[] = ['needs', 'published', 'withheld'];

function byLocale<T extends { en: string; vi: string }>(value: T, locale: string): string {
  return locale === 'vi' ? value.vi : value.en;
}

export function ReviewQueue() {
  const t = useTranslations('Review');
  const locale = useLocale();
  const store = useReviewStore();
  const [tab, setTab] = useState<RunStatus>('needs');
  const [query, setQuery] = useState('');
  const [region, setRegion] = useState('all');
  const [useCase, setUseCase] = useState('all');
  const [urgency, setUrgency] = useState('all');
  const [owner, setOwner] = useState('all');
  const [mine, setMine] = useState(false);

  const counts = useMemo(() => {
    const next: Record<RunStatus, number> = { needs: 0, published: 0, withheld: 0 };
    for (const run of store.runs) next[statusOf(run.id, store.decisions)] += 1;
    return next;
  }, [store.runs, store.decisions]);

  const rows = useMemo(() => {
    const search = query.trim().toLowerCase();

    return store.runs.filter((run) => {
      if (statusOf(run.id, store.decisions) !== tab) return false;
      if (region !== 'all' && run.region.en !== region) return false;
      if (useCase !== 'all' && run.useCase !== useCase) return false;
      if (urgency !== 'all' && run.urgency !== urgency) return false;
      if (owner !== 'all' && !run.owner.includes(owner) && !run.assignee.includes(owner))
        return false;
      if (mine && run.assignee !== PRINCIPAL.name && run.owner !== PRINCIPAL.name) return false;
      if (!search) return true;
      return [run.id, run.useCase, run.useCaseName.en, run.action.en, run.owner, run.assignee]
        .join(' ')
        .toLowerCase()
        .includes(search);
    });
  }, [store.runs, store.decisions, tab, region, useCase, urgency, owner, mine, query]);

  const regions = [...new Set(store.runs.map((run) => run.region.en))];
  const useCases = [...new Set(store.runs.map((run) => run.useCase))];
  const owners = [...new Set(store.runs.flatMap((run) => [run.owner, run.assignee]))];
  const filtered =
    region !== 'all' || useCase !== 'all' || urgency !== 'all' || owner !== 'all' || mine || query;

  function reviewer(run: ReviewRun): string {
    const decision = store.decisions[run.id];
    if (decision) return decision.reviewer;
    return run.assignee === PRINCIPAL.name ? `${run.assignee} · ${t('assignedTag')}` : run.assignee;
  }

  return (
    <div className="tablet:px-5 tablet:py-6 mx-auto flex w-full max-w-400 flex-col gap-4 px-3 py-4">
      <header className="flex flex-col gap-1">
        <h1 className="text-display font-semibold tracking-tight">{t('queue')}</h1>
        <p className="text-body text-ink-muted max-w-3xl">{t('queueSub')}</p>
      </header>

      <div className="border-line flex gap-1 border-b">
        {TABS.map((value) => (
          <button
            key={value}
            type="button"
            onClick={() => setTab(value)}
            aria-pressed={tab === value}
            className={`text-body -mb-px inline-flex items-center gap-1.5 border-b-2 px-2.5 py-2 font-medium ${
              tab === value
                ? 'border-cyan text-ink'
                : 'text-ink-muted hover:text-ink border-transparent'
            }`}
          >
            <AmIcon
              icon={value === 'needs' ? ICON.dot : value === 'published' ? ICON.check : ICON.close}
              size="xs"
            />
            {value === 'needs'
              ? t('needs')
              : value === 'published'
                ? t('published')
                : t('withheld')}
            <span className="text-label text-ink-subtle font-mono">{counts[value]}</span>
          </button>
        ))}
      </div>

      <div className="flex flex-wrap items-end gap-2">
        <label className="relative min-w-56 flex-1">
          <span className="sr-only">{t('search')}</span>
          <AmIcon
            icon={ICON.search}
            size="sm"
            className="text-ink-subtle pointer-events-none absolute top-2.5 left-2.5"
          />
          <input
            type="search"
            id="review-search"
            name="review-search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={t('search')}
            className="border-line-strong bg-raised text-body text-ink placeholder:text-ink-subtle h-9 w-full rounded-md border pr-2.5 pl-8"
          />
        </label>
        <FilterSelect
          label={t('region')}
          value={region}
          onChange={setRegion}
          options={regions}
          all={t('all')}
        />
        <FilterSelect
          label={t('useCase')}
          value={useCase}
          onChange={setUseCase}
          options={useCases}
          all={t('all')}
        />
        <FilterSelect
          label={t('urgency')}
          value={urgency}
          onChange={setUrgency}
          options={['elevated', 'crisis']}
          labels={{ elevated: t('elevatedUrgency'), crisis: t('crisisUrgency') }}
          all={t('all')}
        />
        <FilterSelect
          label={t('owner')}
          value={owner}
          onChange={setOwner}
          options={owners}
          all={t('all')}
        />
        <label className="text-meta text-ink-muted flex h-9 items-center gap-1.5">
          <input
            type="checkbox"
            name="assigned-to-me"
            checked={mine}
            onChange={(event) => setMine(event.target.checked)}
            className="accent-cyan size-3.5"
          />
          {t('assignedMe')}
        </label>
        {filtered && (
          <button
            type="button"
            onClick={() => {
              setQuery('');
              setRegion('all');
              setUseCase('all');
              setUrgency('all');
              setOwner('all');
              setMine(false);
            }}
            className="text-meta text-ink-muted hover:text-ink h-9 px-1 underline-offset-2 hover:underline"
          >
            {t('clear')}
          </button>
        )}
      </div>

      {rows.length === 0 ? (
        <div className="border-line text-meta text-ink-muted rounded-lg border border-dashed px-4 py-10 text-center">
          {filtered ? t('noMatch') : t('emptyQueue')}
        </div>
      ) : (
        <>
          <div className="border-line hidden overflow-x-auto rounded-lg border xl:block">
            <table className="w-full min-w-280 border-collapse text-left">
              <thead>
                <tr className="bg-raised">
                  {[
                    t('run'),
                    t('useCase'),
                    t('region'),
                    t('period'),
                    t('proposed'),
                    t('status'),
                    t('urgency'),
                    t('owner'),
                    t('reviewer'),
                    t('waitTime'),
                    t('updated'),
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
                {rows.map((run) => {
                  const status = statusOf(run.id, store.decisions);
                  return (
                    <tr key={run.id} className="border-line hover:bg-raised border-b last:border-0">
                      <td className="px-2.5 py-2.5 align-top">
                        <Link
                          href={`/review/runs/${run.id}`}
                          className="text-body text-ink font-mono font-semibold whitespace-nowrap underline-offset-2 hover:underline"
                        >
                          {run.id}
                        </Link>
                      </td>
                      <td className="px-2.5 py-2.5 align-top">
                        <span className="text-meta font-mono">{run.useCase}</span>
                        <span className="text-meta text-ink-muted block max-w-40">
                          {byLocale(run.useCaseName, locale)}
                        </span>
                      </td>
                      <td className="text-meta px-2.5 py-2.5 align-top">
                        {byLocale(run.region, locale)}
                      </td>
                      <td className="text-meta px-2.5 py-2.5 align-top">
                        {byLocale(run.period, locale)}
                      </td>
                      <td className="text-meta text-ink-muted max-w-72 px-2.5 py-2.5 align-top">
                        {byLocale(run.action, locale)}
                      </td>
                      <td className="px-2.5 py-2.5 align-top">
                        <StatusChip status={status} />
                      </td>
                      <td className="px-2.5 py-2.5 align-top">
                        <UrgencyChip urgency={run.urgency} />
                      </td>
                      <td className="text-meta px-2.5 py-2.5 align-top">{run.owner}</td>
                      <td className="text-meta text-ink-muted px-2.5 py-2.5 align-top">
                        {reviewer(run)}
                      </td>
                      <td className="text-meta text-ink-subtle px-2.5 py-2.5 align-top">
                        {run.waitingSince === '—'
                          ? '—'
                          : t('waitSince', { time: run.waitingSince })}
                      </td>
                      <td className="text-meta text-ink-subtle px-2.5 py-2.5 align-top font-mono whitespace-nowrap">
                        {utcTime(run.updated)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          <div className="flex flex-col gap-2 xl:hidden">
            {rows.map((run) => {
              const status = statusOf(run.id, store.decisions);
              return (
                <Link
                  key={run.id}
                  href={`/review/runs/${run.id}`}
                  className="border-line bg-panel hover:border-line-strong flex flex-col gap-2 rounded-lg border p-3"
                >
                  <span className="flex flex-wrap items-center gap-2">
                    <span className="text-body font-mono font-semibold">{run.id}</span>
                    <span className="text-label text-ink-subtle font-mono">{run.useCase}</span>
                    <StatusChip status={status} />
                    <UrgencyChip urgency={run.urgency} />
                  </span>
                  <span className="text-body text-ink-muted">{byLocale(run.action, locale)}</span>
                  <span className="text-meta text-ink-subtle flex flex-wrap gap-x-3 gap-y-0.5">
                    <span>{byLocale(run.region, locale)}</span>
                    <span>{byLocale(run.period, locale)}</span>
                    <span>{reviewer(run)}</span>
                  </span>
                </Link>
              );
            })}
          </div>
        </>
      )}

      <p className="text-meta text-ink-subtle">{t('noBulk')}</p>
    </div>
  );
}
