import Image from 'next/image';
import Link from 'next/link';
import { useTranslations } from 'next-intl';

export function BrandGlyph({ large = false }: { large?: boolean }) {
  return (
    <span
      className={`relative block shrink-0 overflow-hidden rounded-sm ${
        large ? 'size-13' : 'size-8'
      }`}
    >
      <Image
        src="/logo.png"
        alt=""
        width={large ? 78 : 48}
        height={large ? 78 : 48}
        className={`absolute max-w-none ${
          large ? '-top-1.5 -left-3.5 h-19 w-19' : '-top-1 -left-2.5 h-12 w-12'
        }`}
      />
    </span>
  );
}

export function BrandMark({ large = false, subtitle }: { large?: boolean; subtitle?: string }) {
  const t = useTranslations('Brand');

  return (
    <Link href="/" className="flex shrink-0 items-center gap-2">
      <BrandGlyph large={large} />
      <span className={`${large ? 'flex' : 'tablet:flex hidden'} flex-col leading-none`}>
        <span className={`${large ? 'text-display' : 'text-title'} font-bold tracking-tight`}>
          <span className="text-fire">Flare</span>
          <span className="text-brand">Chronos</span>
        </span>
        <span
          className={`text-micro text-ink-subtle mt-1 font-mono tracking-widest uppercase ${
            large ? 'max-tablet:hidden' : ''
          }`}
        >
          {subtitle ?? t('product')}
        </span>
      </span>
    </Link>
  );
}
