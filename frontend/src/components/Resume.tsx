import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { fetchResumeMarkdown, resumePdfUrl } from '../lib/api'
import Section from './Section'

type View = 'markdown' | 'pdf'

export default function Resume() {
  const [markdown, setMarkdown] = useState<string | null>(null)
  const [error, setError] = useState(false)
  const [view, setView] = useState<View>('markdown')

  useEffect(() => {
    fetchResumeMarkdown()
      .then(setMarkdown)
      .catch(() => setError(true))
  }, [])

  return (
    <Section id="resume" title="Resume" subtitle="Always the latest version.">
      <div className="mb-6 flex flex-wrap items-center gap-3 text-sm">
        <div className="inline-flex rounded-lg border border-slate-200 p-0.5 dark:border-white/10">
          {(['markdown', 'pdf'] as View[]).map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => setView(option)}
              className={`rounded-md px-3 py-1.5 transition-colors ${
                view === option
                  ? 'bg-accent/10 text-accent dark:text-accent-soft'
                  : 'text-slate-500 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              {option === 'markdown' ? 'Read' : 'PDF'}
            </button>
          ))}
        </div>

        <a
          href={resumePdfUrl}
          download="osher_boudara_resume.pdf"
          className="rounded-lg border border-slate-200 px-3 py-1.5 transition-colors hover:border-accent hover:text-accent dark:border-white/10 dark:hover:border-accent-soft dark:hover:text-accent-soft"
        >
          Download PDF
        </a>
      </div>

      {error && (
        <p className="rounded-xl border border-amber-300/40 bg-amber-50 p-4 text-sm text-amber-900 dark:bg-amber-500/10 dark:text-amber-200">
          The resume couldn’t be loaded right now. Try the PDF, or check back shortly.
        </p>
      )}

      {view === 'pdf' ? (
        <object
          data={resumePdfUrl}
          type="application/pdf"
          className="h-[80vh] w-full rounded-2xl border border-slate-200 dark:border-white/10"
        >
          <p className="p-4 text-sm">
            Your browser can’t display the PDF inline.{' '}
            <a href={resumePdfUrl} className="text-accent underline dark:text-accent-soft">
              Open it in a new tab
            </a>
            .
          </p>
        </object>
      ) : (
        <div className="rounded-2xl border border-slate-200 p-6 sm:p-8 dark:border-white/10">
          {markdown ? (
            <div className="resume-md space-y-4 text-left text-[15px] leading-relaxed">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
            </div>
          ) : (
            !error && (
              <div className="space-y-3">
                {Array.from({ length: 8 }).map((_, i) => (
                  <div
                    key={i}
                    className="h-4 animate-pulse rounded bg-slate-100 dark:bg-white/[0.05]"
                    style={{ width: `${90 - (i % 4) * 15}%` }}
                  />
                ))}
              </div>
            )
          )}
        </div>
      )}
    </Section>
  )
}
