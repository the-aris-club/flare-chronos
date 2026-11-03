'use client';

type Paths = {
  land: string;
  borders: string;
  graticule: string;
  mekong: string;
  amazon: string;
};

export function GlobeFallback({ label, paths }: { label: string; paths: Paths }) {
  return (
    <div className="absolute inset-0">
      <svg
        viewBox="0 0 2048 1024"
        preserveAspectRatio="xMidYMid slice"
        role="img"
        aria-label={label}
        className="size-full"
      >
        <rect width={2048} height={1024} fill="var(--map-ocean)" />
        <path d={paths.land} fill="var(--map-land)" fillRule="evenodd" />
        <path d={paths.graticule} fill="none" stroke="var(--map-grat)" strokeWidth={2} />
        <path d={paths.mekong} fill="var(--amber)" fillOpacity={0.24} />
        <path
          d={paths.mekong}
          fill="none"
          stroke="var(--amber)"
          strokeWidth={4}
          strokeLinejoin="round"
        />
        <path d={paths.amazon} fill="var(--amber)" fillOpacity={0.24} />
        <path
          d={paths.amazon}
          fill="none"
          stroke="var(--amber)"
          strokeWidth={4}
          strokeLinejoin="round"
        />
        <path
          d={paths.borders}
          fill="none"
          stroke="var(--map-border)"
          strokeWidth={2}
          strokeLinejoin="round"
        />
      </svg>

      <p className="text-meta text-ink-subtle bg-panel/90 border-line absolute right-3 bottom-3 rounded-md border px-2 py-1">
        {label}
      </p>
    </div>
  );
}
