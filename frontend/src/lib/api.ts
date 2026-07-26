// In dev, VITE_API_BASE_URL is empty and calls hit the Vite proxy (/api -> :8080).
// In prod (Cloudflare Pages), set VITE_API_BASE_URL to the Cloud Run URL.
export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ""

export interface Repo {
  name: string
  html_url: string
  description: string | null
  language: string[]
  fork: boolean
  stargazers_count: number
  forks_count: number
  created_at: string
  updated_at: string
  created_human: string
  created_relative: string
  updated_human: string
  updated_relative: string
}

export async function fetchRepos(): Promise<Repo[]> {
  const res = await fetch(`${API_BASE}/api/github/repos`)
  if (!res.ok) throw new Error("Failed to load repos")
  const data = await res.json()
  return data.repos as Repo[]
}

export async function fetchResumeMarkdown(): Promise<string> {
  const res = await fetch(`${API_BASE}/api/resume`)
  if (!res.ok) throw new Error("Failed to load resume")
  const data = await res.json()
  return data.markdown as string
}

export const resumePdfUrl = `${API_BASE}/api/resume.pdf`

export interface ChatTurn {
  role: "user" | "assistant"
  content: string
}

// Streams the assistant's reply, calling onDelta for each text chunk.
export async function streamChat(
  message: string,
  history: ChatTurn[],
  onDelta: (text: string) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ message, history }),
    signal,
  })
  if (!res.ok || !res.body) throw new Error("Chat request failed")

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const events = buffer.split("\n\n")
    buffer = events.pop() ?? ""
    for (const event of events) {
      const line = event.trim()
      if (!line.startsWith("data:")) continue
      const json = line.slice(5).trim()
      if (!json) continue
      try {
        const parsed = JSON.parse(json)
        if (parsed.delta) onDelta(parsed.delta as string)
      } catch {
        // ignore malformed chunk
      }
    }
  }
}
