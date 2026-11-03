'use client';

export function FilterSelect({
  label,
  value,
  onChange,
  options,
  labels,
  all,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: string[];
  labels?: Record<string, string>;
  all: string;
}) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-micro text-ink-subtle font-mono uppercase">{label}</span>
      <select
        name={label}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="border-line-strong bg-raised text-meta text-ink h-9 rounded-md border px-2"
      >
        <option value="all">{all}</option>
        {options.map((option) => (
          <option key={option} value={option}>
            {labels?.[option] ?? option}
          </option>
        ))}
      </select>
    </label>
  );
}
