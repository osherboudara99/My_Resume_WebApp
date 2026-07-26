# Migration Context — Streamlit/Lightsail → Cloud Run + Cloudflare Pages

**Purpose:** durable record of the migration plan, decisions, and progress so any
session (or machine) can pick the work up without re-deriving it.

- **Last updated:** 2026-07-25
- **Branch:** `rebuild/cloud-run-react` (off `main`, pushed to origin)
- **Status:** Phase 1 (backend) and Phase 2 (frontend) complete & committed. Phase 3 (deploy) not started.

---

## 1. Goal

Migrate `my-resume-web-app` off the always-on AWS Lightsail box to a cheaper,
scale-to-zero stack, and rebuild both halves:

- **Backend** → clean FastAPI service on **GCP Cloud Run**, with a more reliable Q&A agent.
- **Frontend** → modern **React** app on **Cloudflare Pages**, same features as the
  Streamlit app (resume, certifications, GitHub projects, chat) but a cleaner,
  modern "AI Engineer" look.
- Shut down the Lightsail instance and the keep-alive Lambda when the cutover is done.

## 2. What the old app was

Streamlit multi-page app on Lightsail, domain `osherboudara.com`,
repo `github.com/osherboudara99/my-resume-web-app`.

| Page | Features |
|---|---|
| Home | Animated hero (typed.js rotating titles, social icons), photo + bio, live GitHub repo list (sortable) |
| Resume | Pulled resume from Google Docs at runtime via `gdown` (pdf + md), rendered cleaned markdown, in-page PDF viewer |
| Certifications | 4 cert PDFs (AWS SA, UW ML, AZ-900, USDL DB Tech) with viewers, downloads, credential links |

**The old "Rebbe" agent:** local `sentence-transformers/all-MiniLM-L6-v2` embeddings →
ChromaDB (`db/`) → top-15 retrieval → stuffed into OpenAI `gpt-4o-mini`. Patched with
brittle logic: hardcoded small-talk dict, regex "truncated list" retries, forbidden-entity
blocklist, `<|assistant|>` string scrubbing.

**Pain points the rebuild removes:**
1. `torch` + `sentence-transformers` made the image huge → terrible Cloud Run cold starts,
   and unnecessary: the corpus is only a few KB.
2. Runtime `gdown` Google-Docs download was fragile.
3. Resume-markdown cleanup + agent guardrails were a stack of string hacks.
4. Frontend logic fused to Streamlit.

## 3. Decisions locked in

| Decision | Choice | Why |
|---|---|---|
| Agent model | **Claude Haiku 4.5** (`claude-haiku-4-5`) | $1/M in, $5/M out; best instruction-following per dollar for grounded Q&A. Cheaper per-token options exist (gpt-4o-mini, Gemini Flash-Lite) but the difference is pennies/month at this volume. |
| Retrieval | **Full-context stuffing, no vector DB** | Corpus is ~2.7–4K tokens. Strictly more reliable than RAG at this size, and it deletes the ChromaDB retrain loop entirely. |
| Cost control | Prompt caching + **monthly spend cap** in Anthropic Console + **per-IP rate limit** in FastAPI | The old app died from an exhausted prepaid OpenAI quota — that's a budgeting problem, not a model problem. Cost/question ≈ $0.0055, ~$0.001–0.002 cached. |
| Content freshness | **Model A — live download** | Resume changes frequently. Backend fetches Google Docs each request (TTL-cached ~5 min) with last-known-good + repo copies as fallback. No redeploy to update. |
| Agent name | **"Osher's AI Twin"** (was "Rebbe") | One config string. |
| Frontend | Vite + React + TS + Tailwind v4 | SPA on Cloudflare Pages (free). |
| Routing | `osherboudara.com` → Pages; `api.osherboudara.com` → Cloud Run | |
| Assets folder | `assets/` (renamed from `content/`) | Single source for fallbacks + static assets. |

**Key consequence of full-context stuffing:** there is **no retraining, ever**.
Fetch latest resume → drop into the prompt → answer. `update.py` / ChromaDB is deleted.

## 4. Target architecture

```
                    ┌─────────────────────────────────────┐
   osherboudara.com │        Cloudflare Pages (free)      │
   ────────────────▶│   React SPA (Vite + TS + Tailwind)  │
                    │   hero · chat · projects · resume · │
                    │   certifications  + static PDFs     │
                    └───────────────┬─────────────────────┘
                                    │ HTTPS (fetch / SSE)
                                    ▼
   api.osherboudara.com ┌───────────────────────────────────┐
   ────────────────────▶│      GCP Cloud Run (scale-to-0)   │
                        │      FastAPI backend              │
                        │  POST /api/chat → AI Twin (Haiku) │
                        │  GET /api/github/repos (proxied)  │
                        │  GET /health                      │
                        └──────┬───────────────────┬────────┘
                               │                   │
                    Anthropic API (Haiku)   GitHub API (token server-side)
                    + prompt cache + spend cap
```

**Content flow:**

```
Google Docs (resume)  ─┐
Google Docs (aboutme) ─┼─▶ Cloud Run backend ─▶ • AI Twin context (chat)
                       │   fetch + TTL cache     • Resume page (rendered md + PDF)
assets/ fallbacks ─────┘   + last-known-good
```

- Prompt caching still holds: unchanged resume bytes → cache hits. An edit re-writes
  the cache exactly once, then hits again. "Always live" and "cached/cheap" coexist.
- `aboutme.txt` feeds the AI Twin only — it is **never displayed** on the site.
  It's fetched as **plain text** (`txt`), not markdown, because the Google Doc holds the
  raw markdown pasted as-is; `txt` export returns it verbatim without backslash escapes.

## 5. Current state

### Backend — Phase 1 complete ✅

`backend/` is an **isolated uv project** (its own `pyproject.toml` + `uv.lock`), deliberately
separate from the root `pyproject.toml`, which still holds the old Streamlit deps
(torch, sentence-transformers, chromadb, streamlit, gdown, openai).

| File | Role |
|---|---|
| `backend/app/config.py` | Settings/env. `assets_dir` auto-resolves to `parents[2]/assets` — leave `ASSETS_DIR` **unset** locally; only set it in the container (`/app/assets`). |
| `backend/app/content.py` | Live Google-Docs resume/aboutme fetch, TTL cache, last-known-good + `assets/` fallback |
| `backend/app/github.py` | Cached GitHub repos proxy (token server-side; 60/hr → 5,000/hr) |
| `backend/app/agent.py` | "Osher's AI Twin" on Haiku 4.5 — streaming + prompt caching, guardrails via prompt not string hacks |
| `backend/app/main.py` | FastAPI: `/health`, `POST /api/chat` (SSE), `/api/github/repos`, `/api/resume`, `/api/resume.pdf`; CORS + slowapi rate limit |

**Validated:** app boots, `/health` 200, Anthropic SDK 0.118.0, live resume fetch from
Google Docs (3,900 chars), aboutme loaded (7,095 chars), GitHub proxy returning 18 repos
with languages. Corpus ≈2.7K tokens — below Haiku's 4K cache floor, so caching won't engage
yet; still a fraction of a cent per question.

**Not yet tested live:** the chat agent itself. `backend/.env` now exists locally with keys
(gitignored). Run it with:

```bash
uv run --directory backend uvicorn app.main:app --reload --port 8080
curl -N -X POST localhost:8080/api/chat -H 'content-type: application/json' \
  -d '{"message":"What does Osher do at Cognizant?"}'
```

**Not written yet:** the `Dockerfile` — deliberately held for Phase 3, where the
build-context/assets handling belongs.

### Frontend — Phase 2 complete ✅

Vite + React 19 + TS + Tailwind v4, deps: `@tailwindcss/vite`, framer-motion,
react-markdown, remark-gfm, oxlint. `npm run build` and `npm run lint` both pass.

| File | Role |
|---|---|
| `src/lib/api.ts` | `fetchRepos`, `fetchResumeMarkdown`, `resumePdfUrl`, `streamChat` (SSE reader). Uses `VITE_API_BASE_URL` — empty in dev → Vite proxy. |
| `src/data/site.ts` | All static content: name, rotating titles, socials, bio, certifications list, nav sections |
| `src/components/Nav.tsx` | Sticky nav, blurs/borders on scroll |
| `src/components/Hero.tsx` | Name, rotating title, social icons, photo + bio card |
| `src/components/TypedTitle.tsx` | Type/delete rotation — replaces the old typed.js CDN script |
| `src/components/Section.tsx` | Shared section heading/spacing wrapper |
| `src/components/Projects.tsx` | Live GitHub grid, sort by updated/created/name × asc/desc, skeletons + error state |
| `src/components/Resume.tsx` | Read (markdown) / PDF toggle + download, served from `/api/resume` |
| `src/components/Certifications.tsx` | Accordion with inline PDF viewer, download, credential links |
| `src/components/Chat.tsx` | Floating AI Twin panel — streaming SSE, suggestions, history, graceful failure |

**Config:** `vite.config.ts` has the Tailwind plugin + `/api → localhost:8080` dev proxy.
`index.html` carries the title/description/OG meta and `class="dark"` on `<html>`.

**Static assets** live in `frontend/public/`: `self.jpeg` + `certifications/*.pdf`, copied
from `assets/`. They're served by Pages directly, not through the backend.

⚠️ **Known gap:** the theme is dark-only in practice — `index.html` hardcodes `class="dark"`
and there's no toggle in `Nav.tsx`. The CSS supports both (`@custom-variant dark`), so adding
a toggle is small.

**Root `.gitignore` fix:** the Python template's `lib/` rule was silently ignoring
`frontend/src/lib/`. Scoped to `/lib/` + `/lib64/` (commit `347ecdf`).

### Commits on `rebuild/cloud-run-react`

```
c0803db  feat(frontend): add streaming AI Twin chat panel
5effcdc  feat(frontend): add certifications with inline PDF viewers
02aa89e  feat(frontend): add resume section with markdown and PDF views
7cd7dbc  feat(frontend): add GitHub projects grid with sorting
bdbaeaa  feat(frontend): add hero with rotating titles, socials, and bio
838b16b  feat(frontend): add app shell with sticky section nav
2f88cfb  feat(frontend): add API client for chat, resume, and repos
d48e69b  chore(frontend): add profile photo and certification PDFs
621148d  chore(frontend): scaffold Vite + React + Tailwind app
347ecdf  chore: scope python lib ignore rules to repo root
7353cd3  feat(backend): add FastAPI app with chat, resume, and GitHub endpoints
bbbb4be  feat(backend): add Osher's AI Twin agent on Claude Haiku 4.5
9bcd29b  feat(backend): add cached GitHub repos proxy
ebf2610  feat(backend): add settings and live content fetch
a568065  chore(backend): scaffold isolated uv project
dcf8cdb  chore: content renamed to assets
eb25e67  chore: delete old resume and certs folders
1fbe5e1  feat: scaffold content/ and backend package for the Cloud Run rebuild
bc51fc1  docs(resume): expand aboutme.txt with details from the resume
82194c6  chore: migrate deps to uv and refresh chatbot training (pre-existing WIP)
```

## 6. Content work already done

`assets/aboutme.txt` was expanded from the resume — **purely additive**, nothing removed:

- **Cherre — Data Engineer Intern (May–Aug 2021)** — whole role was missing.
- **Cognizant** enterprise cloud-migration apps: Intake Concierge, LTO Hub (RAG over 500+
  SharePoint docs), Crop Protection Labeler; full tech stack (Python/Google ADK/Vertex AI,
  React/TS, Cloud SQL/GCS/RAG Engine, Terraform/Kubernetes/Artifact Registry, Opik telemetry);
  promotion Associate → Senior Associate (May 2025).
- DSSAT + FastAPI/Pydantic detail on the climate tool; LLM-driven hiring/headcount +
  investment-trend analyses on the competitive-intelligence platform.
- Professional Title line, Key Projects entries, Technical Skills (Databases, AI & Agentic,
  TypeScript, cloud tooling), Education dates (A.S. LAVC June 2020, B.S. CSUN May 2022).

⚠️ **Open nit:** line 11 read `...in recognition of technical excellence ` — looked cut off
(trailing space, `and project leadership` dropped) after a concurrent edit. Worth checking.

## 7. Next steps

1. **Test end-to-end locally.** Run both servers (below) and exercise chat, projects,
   resume, and certifications against the real backend.
2. **Polish:** add a light/dark toggle (see known gap), and consider code-splitting —
   the bundle is ~490 kB (150 kB gzipped), mostly react-markdown.
3. **Phase 3 — deploy.** Backend `Dockerfile` (+ `ASSETS_DIR=/app/assets`) → Cloud Run;
   frontend → Cloudflare Pages; DNS: apex → Pages, `api.` → Cloud Run; secrets into
   Cloud Run (`ANTHROPIC_API_KEY`, `GITHUB_KEY`, Google Doc URLs).
4. **Set the Anthropic Console monthly spend cap.**
5. **Cutover & teardown.** Shut down Lightsail. ✅ Repo-side teardown done: deleted
   `old_lambda_function/` keep-alive hack, the dead Streamlit surface (`Home.py`,
   `pages/`, `chatbot/`, `db/`, `update.py`, `utils/`, `.streamlit/`, root
   `pyproject.toml`/`uv.lock`), plus `app_thumbnail.png` and the Streamlit-only
   `.devcontainer/`.

## 8. Running it locally

Two terminals:

```bash
# backend — http://localhost:8080
uv run --directory backend uvicorn app.main:app --reload --port 8080

# frontend — http://localhost:5173 (proxies /api to :8080)
cd frontend && npm run dev
```

Checks: `cd frontend && npm run build` (tsc + vite) and `npm run lint` (oxlint).

## 9. Working preferences noted

- Branch names: conventional prefix + kebab-case summary (`rebuild/cloud-run-react`).
- Commit in small, logical, step-by-step increments with conventional-commit prefixes.
- **No `Co-Authored-By` trailer** in commit messages.
- Build it together — pause at phase boundaries rather than running ahead.
