import Nav from './components/Nav'
import Hero from './components/Hero'
import { NAME } from './data/site'

export default function App() {
  return (
    <div id="top" className="min-h-svh">
      <Nav />

      <main className="mx-auto max-w-5xl px-6">
        <Hero />
        <section id="projects" className="scroll-mt-20 py-24" />
        <section id="resume" className="scroll-mt-20 py-24" />
        <section id="certifications" className="scroll-mt-20 py-24" />
      </main>

      <footer className="border-t border-slate-200 py-10 text-center text-sm dark:border-white/10">
        <p>
          © {new Date().getFullYear()} {NAME}
        </p>
      </footer>
    </div>
  )
}
