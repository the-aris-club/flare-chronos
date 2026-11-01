'use client';

import { useEffect, useRef } from 'react';
import { useTranslations } from 'next-intl';
import { AmIcon, ICON } from '@/components/ui/icon';

type ReviewDialogProps = {
  title: string;
  subtitle?: string;
  onClose: () => void;
  children: React.ReactNode;
  footer?: React.ReactNode;
  wide?: boolean;
};

export function ReviewDialog({
  title,
  subtitle,
  onClose,
  children,
  footer,
  wide = false,
}: ReviewDialogProps) {
  const panel = useRef<HTMLDivElement>(null);
  const t = useTranslations('Review');

  useEffect(() => {
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', onKeyDown);
    panel.current?.focus();

    return () => {
      document.body.style.overflow = previous;
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [onClose]);

  return (
    <div
      className="bg-scrim fixed inset-0 z-50 flex items-center justify-center p-3"
      role="presentation"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div
        ref={panel}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        tabIndex={-1}
        className={`fc-review-dialog border-line bg-panel flex w-full flex-col overflow-hidden rounded-lg border ${
          wide ? 'max-w-5xl' : 'max-w-2xl'
        }`}
      >
        <header className="border-line flex items-start gap-3 border-b px-4 py-3">
          <div className="min-w-0 flex-1">
            <h2 className="text-subhead font-semibold">{title}</h2>
            {subtitle && <p className="text-meta text-ink-subtle mt-0.5 font-mono">{subtitle}</p>}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label={t('close')}
            className="border-line text-ink-muted hover:bg-chip hover:text-ink inline-flex size-8 shrink-0 items-center justify-center rounded-md border"
          >
            <AmIcon icon={ICON.close} size="sm" />
          </button>
        </header>

        <div className="min-h-0 flex-1 overflow-y-auto p-4">{children}</div>

        {footer && (
          <footer className="border-line bg-raised flex flex-wrap items-center gap-2 border-t px-4 py-2.5">
            {footer}
          </footer>
        )}
      </div>
    </div>
  );
}
