import { useEffect, useState } from 'react'
import { NAME, SECTIONS } from '../data/site'

export default function Nav() {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <header
      className={`sticky top-0 z-50 transition-colors duration-300 ${
        scrolled
          ? 'border-b border-slate-200/80 bg-white/80 backdrop-blur-xl dark:border-white/10 dark:bg-[#0b0b12]/80'
          : 'border-b border-transparent'
      }`}
    >
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <a
          href="#top"
          className="font-mono text-sm tracking-tight text-slate-900 dark:text-slate-100"
        >
          {NAME.toLowerCase().replace(' ', '.')}
          <span className="text-accent">()</span>
        </a>

        <ul className="hidden items-center gap-7 text-sm sm:flex">
          {SECTIONS.map((section) => (
            <li key={section.id}>
              <a
                href={`#${section.id}`}
                className="text-slate-500 transition-colors hover:text-slate-900 dark:text-slate-400 dark:hover:text-white"
              >
                {section.label}
              </a>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  )
}
