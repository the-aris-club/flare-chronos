import type { LucideIcon } from 'lucide-react';
import { AmIcon } from './icon';

export type ChipTone = 'ok' | 'warn' | 'bad' | 'neutral' | 'cyan' | 'purple' | 'raw';

const TONE: Record<ChipTone, string> = {
  ok: 'border-ok text-ok',
  warn: 'border-warn text-warn',
  bad: 'border-bad text-bad',
  neutral: 'border-line-strong text-ink-subtle',
  cyan: 'border-cyan text-cyan',
  purple: 'border-purple text-purple',
  raw: 'border-raw text-raw',
};

export function Chip({
  tone,
  icon,
  children,
}: {
  tone: ChipTone;
  icon?: LucideIcon;
  children: React.ReactNode;
}) {
  return (
    <span
      className={`text-label inline-flex h-5 items-center gap-1 rounded-sm border px-1.5 font-mono font-medium whitespace-nowrap ${TONE[tone]}`}
    >
      {icon && <AmIcon icon={icon} size="xs" />}
      {children}
    </span>
  );
}
