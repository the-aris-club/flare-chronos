'use client';

import { useTranslations } from 'next-intl';
import { FactChip } from './review-bits';
import type { Fact } from '@/data/fixtures/review';

export function VerificationTable({
  facts,
  onFact,
}: {
  facts: Record<string, Fact>;
  onFact?: (key: string) => void;
}) {
  const t = useTranslations('Review');

  return (
    <div className="border-line overflow-x-auto rounded-md border">
      <table className="w-full min-w-160 border-collapse text-left" aria-label={t('verTable')}>
        <thead>
          <tr className="bg-raised">
            {[t('value'), t('unit'), t('srcTool'), t('srcField'), t('status'), t('verdict')].map(
              (label) => (
                <th
                  key={label}
                  scope="col"
                  className="text-label text-ink-muted border-line border-b px-2.5 py-2 font-mono font-medium whitespace-nowrap uppercase"
                >
                  {label}
                </th>
              ),
            )}
          </tr>
        </thead>
        <tbody>
          {Object.values(facts).map((fact) => (
            <tr key={fact.key} className="border-line border-b last:border-0">
              <td className="text-body px-2.5 py-2 font-mono font-semibold">
                {onFact ? (
                  <button
                    type="button"
                    onClick={() => onFact(fact.key)}
                    className="hover:text-cyan text-left underline-offset-2 hover:underline"
                  >
                    {fact.value}
                  </button>
                ) : (
                  fact.value
                )}
              </td>
              <td className="text-meta text-ink-muted px-2.5 py-2">{fact.unit}</td>
              <td className="text-meta px-2.5 py-2 font-mono">{fact.tool}</td>
              <td className="text-meta text-ink-muted px-2.5 py-2 font-mono">{fact.field}</td>
              <td className="px-2.5 py-2">
                <FactChip verdict={fact.verdict} />
              </td>
              <td className="text-meta text-ink-muted px-2.5 py-2">
                {fact.verdict === 'rewritten' && fact.rejected
                  ? `${t('rewritten')} ${fact.rejected} → ${fact.value}`
                  : `${t('acceptedV')} · ${fact.tolerance}`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
