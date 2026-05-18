"use client";

interface Props {
  title: string;
  userName: string;
  onMenuOpen: () => void;
}

function initials(name: string) {
  return name
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}

export default function Header({ title, userName, onMenuOpen }: Props) {
  return (
    <header className="fixed top-0 left-0 md:left-60 right-0 h-14 bg-white border-b border-brand-border flex items-center justify-between px-4 md:px-6 z-30">
      <div className="flex items-center gap-3">
        <button
          onClick={onMenuOpen}
          className="md:hidden p-1.5 rounded-md text-brand-muted hover:text-brand-text hover:bg-brand-raised transition-colors"
          aria-label="Open menu"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h1 className="text-base font-semibold text-brand-text">{title}</h1>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-sm text-brand-muted hidden sm:block">{userName}</span>
        <div className="w-8 h-8 rounded-full bg-teal-600 flex items-center justify-center text-white text-xs font-semibold">
          {initials(userName)}
        </div>
      </div>
    </header>
  );
}
