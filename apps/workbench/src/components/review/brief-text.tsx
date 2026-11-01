'use client';

import { useTranslations } from 'next-intl';
import { AmIcon, ICON } from '@/components/ui/icon';
import type { Fact } from '@/data/fixtures/review';
import type { FactStatus } from '@/lib/workbench/service';

type BriefTextProps = {
  lines: string[];
  facts: Record<string, Fact>;
  showKeys: boolean;
  onFact: (key: string) => void;
  statusFor?: (key: string) => FactStatus;
};

export function BriefText({ lines, facts, showKeys, onFact, statusFor }: BriefTextProps) {
  const t = useTranslations('Briefing.run');
  const review = useTranslations('Review');

  const statusLabel: Record<FactStatus, string> = {
    pending: t('pending'),
    checking: t('checking'),
    verified: review('verified'),
    rewriting: review('rewritten'),
    nosource: review('nosource'),
  };
  const statusIcon = {
    pending: ICON.clock,
    checking: ICON.clock,
    verified: ICON.checkCircle,
    rewriting: ICON.rewrite,
    nosource: ICON.xCircle,
  };
  const statusColor = {
    pending: 'border-line text-ink-subtle',
    checking: 'border-line text-ink-subtle',
    verified: 'border-ok/45 text-ok',
    rewriting: 'border-warn/45 text-warn',
    nosource: 'border-bad/45 text-bad',
  };

  return (
    <div className="flex flex-col gap-3">
      {lines.map((line) => {
        const parts = line.split(/(\{\w+\})/g).filter(Boolean);

        return (
          <p key={line} className="text-body-lg leading-relaxed">
            {parts.map((part) => {
              const match = part.match(/^\{(\w+)\}$/);
              if (!match) return <span key={part}>{part}</span>;

              const key = match[1];
              const fact = facts[key];
              if (!fact) return <span key={part}>{part}</span>;
              const status = statusFor?.(key);

              return (
                <span key={`${line}-${part}`} className="mx-0.5 inline-flex items-baseline gap-1">
                  <button
                    type="button"
                    onClick={() => onFact(key)}
                    aria-label={`${fact.text}. ${fact.tool}.`}
                    className={`border-line-strong bg-raised text-ink hover:border-cyan focus-visible:border-cyan inline-flex items-baseline gap-1 rounded-sm border px-1 text-left font-semibold ${
                      status === 'rewriting' || status === 'nosource' ? 'line-through' : ''
                    }`}
                  >
                    {fact.text}
                    {showKeys && (
                      <span className="text-micro text-ink-subtle font-mono">{fact.call}</span>
                    )}
                  </button>
                  {status && (
                    <span
                      className={`text-micro inline-flex items-center gap-0.5 rounded-sm border px-1 font-mono ${statusColor[status]}`}
                    >
                      <AmIcon icon={statusIcon[status]} size="xs" />
                      {statusLabel[status]}
                    </span>
                  )}
                </span>
              );
            })}
          </p>
        );
      })}
    </div>
  );
}
