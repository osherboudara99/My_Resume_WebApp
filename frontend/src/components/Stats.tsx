import { useEffect, useState } from 'react'
import { fetchGithubStats } from '../lib/api'
import { getLiveMusicPlays } from '../lib/musicStats'
import useCountUp from '../lib/useCountUp'
import Section from './Section'
import TerminalWindow from './TerminalWindow'

function StatCard({
  title,
  value,
  loading,
}: {
  title: string
  value: number
  loading?: boolean
}) {
  const display = useCountUp(loading ? 0 : value)
  return (
    <TerminalWindow title={title}>
      {loading ? (
        <div className="h-10 w-32 animate-pulse rounded-lg bg-slate-200 dark:bg-white/10" />
      ) : (
        <p className="font-mono text-4xl font-semibold tracking-tight text-slate-900 dark:text-slate-100">
          {display.toLocaleString()}
        </p>
      )}
    </TerminalWindow>
  )
}

export default function Stats() {
  const [commits, setCommits] = useState<number | null>(null)
  const [musicPlays, setMusicPlays] = useState(() => getLiveMusicPlays())

  useEffect(() => {
    fetchGithubStats()
      .then((stats) => setCommits(stats.total_commits))
      .catch(() => setCommits(null))
  }, [])

  // Ticks the music stat forward at random moments while the tab is open,
  // matching the same "one at a time throughout the day" drift as the
  // underlying getLiveMusicPlays computation.
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>
    const scheduleNext = () => {
      const delay = 20_000 + Math.random() * 40_000
      timer = setTimeout(() => {
        setMusicPlays(getLiveMusicPlays())
        scheduleNext()
      }, delay)
    }
    scheduleNext()
    return () => clearTimeout(timer)
  }, [])

  return (
    <Section id="stats" title="// stats" subtitle="A few numbers, live from the source.">
      <div className="grid gap-4 sm:grid-cols-2">
        <StatCard title="git log --oneline | wc -l" value={commits ?? 0} loading={commits === null} />
        <StatCard title="music.app --played-count" value={musicPlays} />
      </div>
    </Section>
  )
}
