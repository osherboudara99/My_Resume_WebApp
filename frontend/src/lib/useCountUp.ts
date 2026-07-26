import { useEffect, useRef, useState } from 'react'

// Eases from whatever the last rendered value was up to `target` — re-runs
// smoothly when `target` changes rather than always restarting from 0.
export default function useCountUp(target: number, duration = 1200): number {
  const [value, setValue] = useState(0)
  const fromRef = useRef(0)

  useEffect(() => {
    const from = fromRef.current
    if (from === target) {
      setValue(target)
      return
    }

    const start = performance.now()
    let raf: number

    function tick(now: number) {
      const progress = Math.min((now - start) / duration, 1)
      const eased = 1 - (1 - progress) ** 3
      setValue(Math.round(from + (target - from) * eased))
      if (progress < 1) {
        raf = requestAnimationFrame(tick)
      } else {
        fromRef.current = target
      }
    }

    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [target, duration])

  return value
}
