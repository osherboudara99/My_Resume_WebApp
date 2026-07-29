import { APPLE_MUSIC_BASE_DATE, APPLE_MUSIC_TOTAL_PLAYS } from '../data/site'

// Deterministic PRNG (mulberry32) so the same date always produces the same
// "random" sequence — every visitor sees the same number on a given day.
function mulberry32(seed: number) {
  let state = seed | 0
  return () => {
    state = (state + 0x6d2b79f5) | 0
    let t = Math.imul(state ^ (state >>> 15), 1 | state)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function hashString(value: string): number {
  let hash = 0
  for (let i = 0; i < value.length; i++) {
    hash = (Math.imul(31, hash) + value.charCodeAt(i)) | 0
  }
  return hash
}

function dateKey(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

// A given calendar day always "listens to" the same random amount, between
// 5 and 25 plays, so the total keeps drifting forward day over day. The draw is
// squared to skew it toward the low end: the median day lands on 10 rather than
// the 15 a flat 5-25 spread would give, with the heavier days as the tail.
function dailyIncrementTarget(key: string): number {
  const rand = mulberry32(hashString(key))
  const skewed = rand() ** 2
  return 5 + Math.floor(skewed * 21)
}

// Reveals today's increment one tick at a time at random moments through the
// day, rather than jumping straight to the daily target at midnight.
function ticksElapsedToday(key: string, target: number, now: Date): number {
  const rand = mulberry32(hashString(key) ^ 0x9e3779b9)
  const minuteOfDay = now.getHours() * 60 + now.getMinutes()
  let elapsed = 0
  for (let i = 0; i < target; i++) {
    if (Math.floor(rand() * 1440) <= minuteOfDay) elapsed++
  }
  return elapsed
}

// Grows APPLE_MUSIC_TOTAL_PLAYS forward from APPLE_MUSIC_BASE_DATE: one
// deterministic daily increment per full day elapsed, plus a partial
// increment for today based on how much of the day has passed.
export function getLiveMusicPlays(now: Date = new Date()): number {
  const base = new Date(`${APPLE_MUSIC_BASE_DATE}T00:00:00`)
  let total = APPLE_MUSIC_TOTAL_PLAYS

  const cursor = new Date(base)
  while (dateKey(cursor) < dateKey(now)) {
    total += dailyIncrementTarget(dateKey(cursor))
    cursor.setDate(cursor.getDate() + 1)
  }

  const todayKey = dateKey(now)
  total += ticksElapsedToday(todayKey, dailyIncrementTarget(todayKey), now)

  return total
}
