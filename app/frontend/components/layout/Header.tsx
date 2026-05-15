"use client";

interface Props {
  title: string;
  userName: string;
}

function initials(name: string) {
  return name
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();
}

export default function Header({ title, userName }: Props) {
  return (
    <header className="fixed top-0 left-60 right-0 h-14 bg-white border-b border-brand-border flex items-center justify-between px-6 z-30">
      <h1 className="text-base font-semibold text-brand-text">{title}</h1>
      <div className="flex items-center gap-3">
        <span className="text-sm text-brand-muted hidden sm:block">{userName}</span>
        <div className="w-8 h-8 rounded-full bg-teal-600 flex items-center justify-center text-white text-xs font-semibold">
          {initials(userName)}
        </div>
      </div>
    </header>
  );
}
