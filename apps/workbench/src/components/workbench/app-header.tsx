'use client';

import { useCallback, useState } from 'react';
import Link from 'next/link';
import { useService } from '@/components/service/service-provider';
import { useTranslations } from 'next-intl';
import { Icon, ICON } from '@/components/ui/icon';
import { BrandMark } from '@/components/ui/brand-mark';
import { HeaderBar } from '@/components/ui/header-bar';
import { LocaleToggle } from '@/components/ui/locale-toggle';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import type { RegionId } from '@/lib/calendar/types';

type AppHeaderProps = {
  region: RegionId;
  period: { start: number; end: number };
  briefingOpen: boolean;
  onRegion: (region: RegionId) => void;
  onTour: () => void;
  onEvidence: () => void;
  onBriefing: () => void;
  onService: () => void;
};

const buttonClass =
  'inline-flex h-7 items-center gap-1.5 rounded-md border border-line-strong px-2 text-meta font-medium text-ink hover:bg-chip';

export function AppHeader({
  region,
  period,
  briefingOpen,
  onRegion,
  onTour,
  onEvidence,
  onBriefing,
  onService,
}: AppHeaderProps) {
  const t = useTranslations('Header');
  const review = useTranslations('Review');
  const reviewStore = useService();
  const [menuOpen, setMenuOpen] = useState(false);
  const connected = reviewStore.connection === 'connected';
  const down = reviewStore.connection === 'unavailable';
  const serviceLabel = down
    ? t('serviceDown')
    : !connected
      ? t('serviceNotConnected')
      : t('serviceUp');
  const serviceTone = down
    ? 'border-bad/50 text-bad'
    : !connected
      ? 'border-line text-ink-subtle'
      : 'border-ok/45 text-ok';

  const handleRegionChange = useCallback(
    (event: React.ChangeEvent<HTMLSelectElement>) => onRegion(event.target.value as RegionId),
    [onRegion],
  );
  const toggleMenu = useCallback(() => setMenuOpen((value) => !value), []);
  const closeMenu = useCallback(() => setMenuOpen(false), []);
  const handleServiceMenu = useCallback(() => {
    setMenuOpen(false);
    onService();
  }, [onService]);
  const handleTourMenu = useCallback(() => {
    setMenuOpen(false);
    onTour();
  }, [onTour]);
  const handleEvidenceMenu = useCallback(() => {
    setMenuOpen(false);
    onEvidence();
  }, [onEvidence]);
  const handleBriefingMenu = useCallback(() => {
    setMenuOpen(false);
    onBriefing();
  }, [onBriefing]);

  return (
    <HeaderBar>
      <BrandMark />

      <span aria-hidden="true" className="bg-line-strong tablet:block mx-1 hidden h-6 w-px" />

      <label className="relative inline-flex items-center">
        <span className="sr-only">{t('region')}</span>
        <select
          id="region"
          name="region"
          autoComplete="off"
          value={region}
          onChange={handleRegionChange}
          className="border-line-strong bg-raised text-body text-ink tablet:max-w-56 max-tablet:max-w-none max-tablet:flex-1 h-8 max-w-44 appearance-none truncate rounded-md border py-0 pr-7 pl-2.5 font-medium"
        >
          <option value="mekong">{t('regions.mekongLong')}</option>
          <option value="amazon">{t('regions.amazonLong')}</option>
        </select>
        <Icon
          icon={ICON.chevron}
          size="sm"
          className="text-ink-subtle pointer-events-none absolute right-2"
        />
      </label>

      <span className="border-line text-body text-ink-muted hidden h-7 items-center gap-1.5 rounded-md border px-2.5 xl:inline-flex">
        <span className="text-micro text-ink-subtle font-mono tracking-widest uppercase">
          {t('period')}
        </span>
        <span className="text-ink font-mono">
          {t('periodValue', { start: period.start, end: period.end })}
        </span>
      </span>

      <div className="hidden items-center gap-1.5 xl:flex">
        <button
          type="button"
          onClick={onTour}
          aria-label={t('walkthrough')}
          title={t('walkthrough')}
          className={buttonClass}
        >
          <Icon icon={ICON.tour} size="sm" />
          <span className="hidden xl:inline">{t('walkthrough')}</span>
        </button>
        <button
          type="button"
          onClick={onEvidence}
          aria-label={t('evidence')}
          title={t('evidence')}
          className={buttonClass}
        >
          <Icon icon={ICON.evidence} size="sm" />
          <span className="hidden xl:inline">{t('evidence')}</span>
        </button>
        <button
          type="button"
          onClick={onBriefing}
          aria-pressed={briefingOpen}
          aria-label={t('briefing')}
          title={t('briefing')}
          className={`${buttonClass} ${briefingOpen ? 'bg-seg' : ''}`}
        >
          <Icon icon={ICON.briefing} size="sm" />
          <span className="hidden xl:inline">{t('briefing')}</span>
        </button>
        <Link href="/" aria-label={t('globe')} title={t('globe')} className={buttonClass}>
          <Icon icon={ICON.globe} size="sm" />
          <span className="hidden xl:inline">{t('globe')}</span>
        </Link>
      </div>

      <div className="ml-auto flex items-center gap-2">
        <button
          type="button"
          onClick={onBriefing}
          aria-pressed={briefingOpen}
          aria-label={t('briefing')}
          title={t('briefing')}
          className="border-line-strong text-ink hover:bg-chip text-meta tablet:inline-flex hidden h-7 items-center gap-1.5 rounded-md border px-2 font-medium xl:hidden"
        >
          <Icon icon={ICON.briefing} size="sm" />
        </button>
        <Link
          href="/review"
          title={review('review')}
          className="border-line-strong text-ink hover:bg-chip text-meta tablet:inline-flex hidden h-7 items-center gap-1.5 rounded-md border px-2 font-medium"
        >
          <Icon icon={ICON.review} size="sm" />
          <span>{review('review')}</span>
          {reviewStore.needsDecision > 0 && (
            <span className="bg-cyan text-canvas text-micro inline-flex h-4 min-w-4 items-center justify-center rounded-full px-1 font-mono font-semibold">
              {reviewStore.needsDecision}
            </span>
          )}
        </Link>
        <button
          type="button"
          onClick={onService}
          title={t('serviceStatus')}
          aria-label={`${t('serviceStatus')}: ${serviceLabel}`}
          className={`tablet:inline-flex text-micro hidden h-7 items-center gap-1.5 rounded-md border px-2 font-mono ${serviceTone}`}
        >
          <Icon icon={down ? ICON.xCircle : ICON.service} size="sm" />
          <span className="xl:hidden">
            {down
              ? t('serviceShortDown')
              : !connected
                ? t('serviceShortNotConnected')
                : t('serviceShortUp')}
          </span>
          <span className="hidden xl:inline">{serviceLabel}</span>
        </button>
        <LocaleToggle />
        <ThemeToggle />

        <div className="relative xl:hidden">
          <button
            type="button"
            onClick={toggleMenu}
            aria-label={t('menu')}
            aria-expanded={menuOpen}
            className={buttonClass}
          >
            <Icon icon={ICON.menu} size="sm" />
          </button>
          {menuOpen && (
            <div className="border-line bg-panel absolute top-full right-0 z-50 mt-1 flex w-44 flex-col rounded-md border p-1">
              <button
                type="button"
                onClick={handleServiceMenu}
                className="text-body text-ink hover:bg-chip rounded-sm px-2 py-1.5 text-left"
              >
                {serviceLabel}
              </button>
              <button
                type="button"
                onClick={handleTourMenu}
                className="text-body text-ink hover:bg-chip rounded-sm px-2 py-1.5 text-left"
              >
                {t('walkthrough')}
              </button>
              <button
                type="button"
                onClick={handleEvidenceMenu}
                className="text-body text-ink hover:bg-chip rounded-sm px-2 py-1.5 text-left"
              >
                {t('evidence')}
              </button>
              <button
                type="button"
                onClick={handleBriefingMenu}
                className="text-body text-ink hover:bg-chip rounded-sm px-2 py-1.5 text-left"
              >
                {t('briefing')}
              </button>
              <Link
                href="/review"
                onClick={closeMenu}
                className="text-body text-ink hover:bg-chip flex items-center justify-between rounded-sm px-2 py-1.5 text-left"
              >
                {review('review')}
                {reviewStore.needsDecision > 0 && (
                  <span className="bg-cyan text-canvas text-micro inline-flex h-4 min-w-4 items-center justify-center rounded-full px-1 font-mono font-semibold">
                    {reviewStore.needsDecision}
                  </span>
                )}
              </Link>
              <Link
                href="/"
                onClick={closeMenu}
                className="text-body text-ink hover:bg-chip rounded-sm px-2 py-1.5 text-left"
              >
                {t('globe')}
              </Link>
            </div>
          )}
        </div>
      </div>
    </HeaderBar>
  );
}
