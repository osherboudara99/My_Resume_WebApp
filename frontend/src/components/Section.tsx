import type { ReactNode } from 'react'

interface Props {
  id: string
  title: string
  subtitle?: ReactNode
  children: ReactNode
}

export default function Section({ id, title, subtitle, children }: Props) {
  return (
    <section id={id} className="scroll-mt-20 border-t border-slate-200 py-20 dark:border-white/10">
      <h2 className="text-3xl font-semibold tracking-tight">
        <span className="mr-2 font-mono text-accent dark:text-accent-soft" aria-hidden="true">
          //
        </span>
        {title}
      </h2>
      {subtitle && <p className="mt-2 text-[15px]">{subtitle}</p>}
      <div className="mt-10">{children}</div>
    </section>
  )
}
