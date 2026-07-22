# Backend — Osher's AI Twin API

FastAPI service for the rebuilt portfolio. Runs on Cloud Run (scale-to-zero).
It serves the chat agent plus live resume/GitHub data to the React frontend.

## What it does

- **`POST /api/chat`** — streams answers from *Osher's AI Twin* (Claude Haiku 4.5).
  The full resume + aboutme corpus is passed as context (no vector DB, no
  retraining), so answers always reflect the latest resume.
- **`GET /api/github/repos`** — cached GitHub repos (token stays server-side).
- **`GET /api/resume`** — latest resume as markdown (live from Google Docs).
- **`GET /api/resume.pdf`** — latest resume PDF (live from Google Docs).
- **`GET /health`** — liveness check.

Resume/aboutme are fetched fresh from Google Docs with a short TTL cache and fall
back to the bundled copies in `../assets/` if a fetch fails.

## Run locally

```bash
# from repo root
cp backend/.env.example backend/.env   # then add your ANTHROPIC_API_KEY
uv sync --directory backend
uv run --directory backend uvicorn app.main:app --reload --port 8080
```

Then:

```bash
curl localhost:8080/health
curl localhost:8080/api/github/repos
curl -N -X POST localhost:8080/api/chat \
  -H 'content-type: application/json' \
  -d '{"message":"What does Osher do at Cognizant?"}'
```

## Configuration

All settings come from environment variables (see `.env.example`). Key ones:

| Var | Purpose |
| --- | --- |
| `ANTHROPIC_API_KEY` | Required for the chat agent |
| `ANTHROPIC_MODEL` | Defaults to `claude-haiku-4-5` |
| `GITHUB_KEY` | Optional; avoids GitHub's 60 req/hr unauth limit |
| `GOOGLE_DOC_RESUME_URL` | Link-shared Google Doc for the live resume |
| `GOOGLE_DOC_ABOUTME_URL` | Optional; live aboutme (else uses `assets/aboutme.txt`) |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins (the frontend) |
| `CHAT_RATE_LIMIT` | Per-IP limit on `/api/chat`, e.g. `20/minute` |

## Layout

```
backend/
  app/
    config.py    settings
    content.py   live resume/aboutme fetch (TTL cache + fallback)
    github.py    cached GitHub repos proxy
    agent.py     Osher's AI Twin (Haiku 4.5, streaming + prompt caching)
    main.py      FastAPI app + routes
  pyproject.toml / uv.lock   isolated backend deps (uv)
```
