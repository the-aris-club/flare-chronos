'use client';

type SegmentedOption<T extends string> = {
  value: T;
  label: string;
  title?: string;
};

type SegmentedControlProps<T extends string> = {
  label: string;
  value: T;
  options: readonly SegmentedOption<T>[];
  onChange: (value: T) => void;
};

export function SegmentedControl<T extends string>({
  label,
  value,
  options,
  onChange,
}: SegmentedControlProps<T>) {
  return (
    <div
      role="group"
      aria-label={label}
      className="border-line-strong inline-flex gap-0.5 rounded-md border p-0.5"
    >
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          aria-pressed={value === option.value}
          title={option.title}
          className={`text-meta h-6 rounded-sm px-2 font-mono font-semibold transition-colors ${
            value === option.value ? 'bg-seg text-ink' : 'text-ink-subtle hover:text-ink'
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
