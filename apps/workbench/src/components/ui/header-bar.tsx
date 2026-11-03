export function HeaderBar({ children }: { children: React.ReactNode }) {
  return (
    <header className="border-line bg-surface tablet:px-4 sticky top-0 z-40 flex h-14 items-center gap-2 border-b px-3 xl:h-13 xl:px-5">
      {children}
    </header>
  );
}
