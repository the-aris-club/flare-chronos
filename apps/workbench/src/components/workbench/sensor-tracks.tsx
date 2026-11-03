'use client';

const SENSORS = [
  { name: 'Terra', from: 2000 },
  { name: 'Aqua', from: 2002 },
  { name: 'Suomi-NPP', from: 2012 },
  { name: 'NOAA-20', from: 2020 },
  { name: 'NOAA-21', from: 2024 },
];

export function SensorTracks({ years }: { years: number[] }) {
  const first = years[0] ?? 2000;
  const last = years.at(-1) ?? first;
  const span = Math.max(1, last - first + 1);

  return (
    <div className="px-3 pb-1" aria-label="Sensor coverage">
      <div className="flex flex-col gap-0.5">
        {SENSORS.map((sensor) => {
          const start = Math.max(0, sensor.from - first);
          return (
            <div key={sensor.name} className="flex items-center gap-2">
              <span className="text-micro text-ink-subtle w-16 font-mono">{sensor.name}</span>
              <svg
                viewBox={`0 0 ${span} 2`}
                preserveAspectRatio="none"
                className="h-1.5 flex-1"
                aria-hidden="true"
              >
                <title>{sensor.name}</title>
                <rect width={span} height={2} fill="var(--line)" opacity={0.35} />
                <rect
                  x={start}
                  width={Math.max(0, span - start)}
                  height={2}
                  fill="var(--teal)"
                  opacity={0.5}
                />
              </svg>
            </div>
          );
        })}
      </div>
    </div>
  );
}
