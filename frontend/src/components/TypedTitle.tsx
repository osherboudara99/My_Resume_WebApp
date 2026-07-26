import { useEffect, useState } from 'react'

interface Props {
  strings: string[]
  typeSpeed?: number
  backSpeed?: number
  backDelay?: number
}

/**
 * Types each string out, pauses, deletes it, then moves to the next — the
 * replacement for the old typed.js CDN script.
 */
export default function TypedTitle({
  strings,
  typeSpeed = 90,
  backSpeed = 40,
  backDelay = 1400,
}: Props) {
  const [index, setIndex] = useState(0)
  const [text, setText] = useState('')
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    const full = strings[index % strings.length]

    if (!deleting && text === full) {
      const timer = setTimeout(() => setDeleting(true), backDelay)
      return () => clearTimeout(timer)
    }

    if (deleting && text === '') {
      setDeleting(false)
      setIndex((i) => (i + 1) % strings.length)
      return
    }

    const timer = setTimeout(
      () =>
        setText((current) =>
          deleting ? full.slice(0, current.length - 1) : full.slice(0, current.length + 1),
        ),
      deleting ? backSpeed : typeSpeed,
    )
    return () => clearTimeout(timer)
  }, [text, deleting, index, strings, typeSpeed, backSpeed, backDelay])

  return (
    <span>
      <span className="text-gradient font-medium">{text}</span>
      <span className="animate-caret ml-0.5 text-accent" aria-hidden="true">
        |
      </span>
    </span>
  )
}
