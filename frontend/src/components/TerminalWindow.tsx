import type { ReactNode } from 'react'

interface Props {
  title: string
  children: ReactNode
  className?: string
}

export default function TerminalWindow({ title, children, className = '' }: Props) {
  return (
    <div
      className={`overflow-hidden rounded-2xl border border-slate-200 bg-slate-50/60 dark:border-white/10 dark:bg-white/[0.03] ${className}`}
    >
      <div className="flex items-center gap-2 border-b border-slate-200 bg-slate-100/80 px-4 py-2.5 dark:border-white/10 dark:bg-white/[0.04]">
        <span className="flex gap-1.5" aria-hidden="true">
          <span className="size-2.5 rounded-full bg-red-400/70" />
          <span className="size-2.5 rounded-full bg-amber-400/70" />
          <span className="size-2.5 rounded-full bg-emerald-400/70" />
        </span>
        <span className="ml-1 truncate font-mono text-xs text-slate-500 dark:text-slate-400">
          {title}
        </span>
      </div>
      <div className="p-5">{children}</div>
    </div>
  )
}
