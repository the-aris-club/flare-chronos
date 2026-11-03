'use client';

import { useTranslations } from 'next-intl';
import type { EvidenceColumn } from '@/lib/workbench/evidence-tables';

export function EvidenceTable({
  caption,
  columns,
  rows,
}: {
  caption: string;
  columns: EvidenceColumn[];
  rows: string[][];
}) {
  const t = useTranslations('Evidence');

  return (
    <details className="border-line rounded-md border">
      <summary className="text-meta text-ink-muted hover:text-ink cursor-pointer px-2.5 py-1.5">
        {t('viewData')}
      </summary>
      <div className="border-line max-h-64 overflow-auto border-t">
        <table className="w-full border-collapse text-left">
          <caption className="text-meta text-ink-muted px-2.5 py-2 text-left font-medium">
            {caption}
          </caption>
          <thead>
            <tr className="bg-raised">
              {columns.map((column) => (
                <th
                  key={column.label}
                  scope="col"
                  className={`text-label text-ink-subtle border-line border-b px-2.5 py-1.5 font-mono font-medium whitespace-nowrap ${
                    column.align === 'right' ? 'text-right' : 'text-left'
                  }`}
                >
                  {column.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.join('|')} className="border-line border-b last:border-0">
                {row.map((cell, index) => (
                  <td
                    key={`${columns[index]?.label}-${cell}`}
                    className={`text-meta px-2.5 py-1.5 font-mono ${
                      columns[index]?.align === 'right' ? 'text-right' : 'text-left'
                    }`}
                  >
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </details>
  );
}
