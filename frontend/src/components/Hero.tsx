import { motion } from 'framer-motion'
import TypedTitle from './TypedTitle'
import { BIO, NAME, SOCIALS, TITLES, TWIN_NAME } from '../data/site'

function LinkedInIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="size-5" aria-hidden="true">
      <path d="M4.98 3.5C4.98 4.88 3.87 6 2.5 6S0 4.88 0 3.5 1.12 1 2.5 1 4.98 2.12 4.98 3.5zM0 24h5V7H0v17zm7.5-17h4.7v2.5h.07c.66-1.25 2.3-2.5 4.73-2.5 5.05 0 5.98 3.32 5.98 7.63V24h-5v-7.33c0-1.75-.03-4-2.43-4s-2.8 1.9-2.8 3.87V24h-5V7z" />
    </svg>
  )
}

function GitHubIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="size-5" aria-hidden="true">
      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.3 3.44 9.8 8.2 11.3.6.1.8-.26.8-.57v-2.1c-3.1.7-3.8-1.3-3.8-1.3-.6-1.4-1.4-1.8-1.4-1.8-1.1-.7.1-.7.1-.7 1.2.1 1.8 1.3 1.8 1.3 1.1 1.8 2.8 1.3 3.5 1 .1-.8.4-1.4.7-1.7-2.7-.3-5.5-1.3-5.5-6 0-1.3.5-2.4 1.3-3.3-.2-.3-.6-1.6.2-3.3 0 0 1-.4 3.1 1.1a10.9 10.9 0 0 1 5.6 0c2.1-1.5 3.1-1.1 3.1-1.1.8 1.7.4 3 .2 3.3.8.9 1.3 2 1.3 3.3 0 4.7-2.8 5.7-5.5 6 .5.4.9 1.1.9 2.1v3.1c0 .31.2.68.8.57C20.56 21.8 24 17.3 24 12c0-6.63-5.37-12-12-12z" />
    </svg>
  )
}

export default function Hero() {
  return (
    <section id="about" className="relative scroll-mt-20 pt-16 pb-24">
      <div
        className="glow-accent pointer-events-none absolute inset-x-0 -top-32 h-[32rem]"
        aria-hidden="true"
      />

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative text-center"
      >
        <h1 className="text-5xl font-semibold tracking-tight sm:text-6xl">{NAME}</h1>

        <p className="mt-4 text-lg sm:text-xl">
          I am <TypedTitle strings={TITLES} />
        </p>

        <div className="mt-7 flex items-center justify-center gap-3">
          <a
            href={SOCIALS.linkedin}
            target="_blank"
            rel="noreferrer"
            aria-label="LinkedIn"
            className="rounded-xl border border-slate-200 p-2.5 text-slate-600 transition-colors hover:border-accent hover:text-accent dark:border-white/10 dark:text-slate-300 dark:hover:border-accent-soft dark:hover:text-accent-soft"
          >
            <LinkedInIcon />
          </a>
          <a
            href={SOCIALS.github}
            target="_blank"
            rel="noreferrer"
            aria-label="GitHub"
            className="rounded-xl border border-slate-200 p-2.5 text-slate-600 transition-colors hover:border-accent hover:text-accent dark:border-white/10 dark:text-slate-300 dark:hover:border-accent-soft dark:hover:text-accent-soft"
          >
            <GitHubIcon />
          </a>
        </div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.15 }}
        className="relative mt-16 flex flex-col items-center gap-8 rounded-2xl border border-slate-200 bg-slate-50/60 p-8 sm:flex-row sm:items-start dark:border-white/10 dark:bg-white/[0.03]"
      >
        <img
          src="/self.jpeg"
          alt={NAME}
          width={200}
          height={200}
          className="size-44 shrink-0 rounded-2xl object-cover shadow-lg"
        />
        <div className="space-y-4 text-left text-[15px] leading-relaxed">
          {BIO.map((paragraph) => (
            <p key={paragraph.slice(0, 32)}>{paragraph}</p>
          ))}
          <p>
            Feel free to chat with <span className="text-slate-900 dark:text-slate-100">{TWIN_NAME}</span>{' '}
            to learn more about my work and projects.
          </p>
        </div>
      </motion.div>
    </section>
  )
}
