'use client';

import { useTranslations } from 'next-intl';
import type { ReviewFact } from '@/lib/review/api';

export function VerificationTable({ facts }: { facts: ReviewFact[] }) {
  const t = useTranslations('Review');

  return (
    <div className="border-line overflow-x-auto rounded-md border">
      <table className="w-full min-w-120 border-collapse text-left" aria-label={t('verTable')}>
        <thead>
          <tr className="bg-raised">
            {[t('factKey'), t('value'), t('unit'), t('srcTool'), t('provTag')].map((label) => (
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
          {facts.map((fact) => (
            <tr key={fact.key} className="border-line border-b last:border-0">
              <td className="text-meta px-2.5 py-2 font-mono">{fact.key}</td>
              <td className="text-body px-2.5 py-2 font-mono font-semibold">{fact.value}</td>
              <td className="text-meta text-ink-muted px-2.5 py-2">{fact.unit}</td>
              <td className="text-meta px-2.5 py-2 font-mono">{fact.tool}</td>
              <td className="text-meta text-ink-muted px-2.5 py-2 font-mono">{fact.provenance}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
