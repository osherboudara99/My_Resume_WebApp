# Deployment — Cloud Run (API) + Cloudflare Pages (site)

Replaces the always-on Lightsail box. Cloud Run scales to zero, Pages is free.

## Deployed instance (as of 2026-07-25)

| | |
|---|---|
| Project | `resume-site-503602` (number `374199633508`) |
| Region | `us-west1` |
| Service | `osher-ai-twin` |
| **API URL** | `https://osher-ai-twin-374199633508.us-west1.run.app` |
| Image | `us-west1-docker.pkg.dev/resume-site-503602/containers/osher-ai-twin:20260725-1955` |
| Runtime SA | `osher-ai-twin-run@resume-site-503602.iam.gserviceaccount.com` |
| Secrets | `anthropic-api-key`, `github-key` (Secret Manager) |

Verified live: `/health`, `/api/github/repos` (19 repos, authenticated), `/api/resume`
(live from Google Docs), and streaming `/api/chat`.

**Still to do:** Cloudflare Pages (§5), then add its origin to `ALLOWED_ORIGINS`.

> **Run these in Git Bash, not PowerShell.** They use `$VAR`, `printf`, and `\`
> line continuations. In PowerShell they will fail or, worse, half-succeed.

Fill these in once and reuse them below:

```bash
PROJECT=osher-portfolio   # must be globally unique; append digits if taken
REGION=us-west1           # closest to LA
REPO=containers           # Artifact Registry repo name
SERVICE=osher-ai-twin
IMAGE="$REGION-docker.pkg.dev/$PROJECT/$REPO/$SERVICE:$(date +%Y%m%d-%H%M)"
```

## 1. One-time GCP setup

Create a dedicated project rather than reusing an existing one — it keeps billing
and IAM clean, and teardown is one command.

```bash
gcloud projects create "$PROJECT" --name="Portfolio Site"
gcloud config set project "$PROJECT"

# Billing MUST be linked or `services enable` fails with a vague permission error.
gcloud billing accounts list                       # copy the ACCOUNT_ID
gcloud billing projects link "$PROJECT" --billing-account=ACCOUNT_ID

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com

gcloud artifacts repositories create "$REPO" \
  --repository-format=docker --location="$REGION" \
  --description="Container images for the portfolio site"

gcloud auth configure-docker "$REGION-docker.pkg.dev"
```

Then create a dedicated runtime service account. Cloud Run would otherwise use the
default compute SA, which is over-privileged (and may not exist in a fresh project).

```bash
SA="$SERVICE-run@$PROJECT.iam.gserviceaccount.com"
gcloud iam service-accounts create "$SERVICE-run" --display-name="Cloud Run runtime"
```

## 2. Secrets

Keys never go in the image or in `gcloud run deploy --set-env-vars`. Put them in
Secret Manager and mount them as env vars.

```bash
printf %s "sk-ant-..."      | gcloud secrets create anthropic-api-key --data-file=-
printf %s "github_pat_..."  | gcloud secrets create github-key       --data-file=-

# Let the runtime service account read them
for s in anthropic-api-key github-key; do
  gcloud secrets add-iam-policy-binding "$s" \
    --member="serviceAccount:$SA" \
    --role=roles/secretmanager.secretAccessor
done
```

To rotate later: `printf %s "new-value" | gcloud secrets versions add anthropic-api-key --data-file=-`

## 3. Build and push the image

The build context is the **repo root** (the image needs `assets/`), with the
Dockerfile in `backend/`.

```bash
docker build -f backend/Dockerfile -t "$IMAGE" .
docker push "$IMAGE"
```

Verify locally first if you changed anything:

```bash
docker run --rm -p 8099:8080 --env-file backend/.env "$IMAGE"
curl localhost:8099/health
```

*Alternative — no local Docker:* `gcloud builds submit --config cloudbuild.yaml
--substitutions=_IMAGE="$IMAGE"`. Add a `.gcloudignore` first, or the upload will
include `node_modules/`, `.venv/`, and the ChromaDB binaries.

## 4. Deploy to Cloud Run

`ALLOWED_ORIGINS` contains commas, and `--set-env-vars` splits on commas by default —
passing it plainly would create a bogus second env var and silently break CORS. The
`^##^` prefix switches the delimiter to `##`:

```bash
gcloud run deploy "$SERVICE" \
  --image="$IMAGE" \
  --region="$REGION" \
  --platform=managed \
  --service-account="$SA" \
  --allow-unauthenticated \
  --min-instances=0 \
  --max-instances=3 \
  --memory=512Mi \
  --cpu=1 \
  --concurrency=40 \
  --timeout=120 \
  --set-env-vars="^##^ASSETS_DIR=/app/assets##ANTHROPIC_MODEL=claude-haiku-4-5##MAX_TOKENS=700##GITHUB_USERNAME=osherboudara99##CONTENT_TTL_SECONDS=300##CHAT_RATE_LIMIT=20/minute##GOOGLE_DOC_RESUME_URL=https://docs.google.com/document/d/1gql8n7U8WHkdLEu6R6wFI41tLWpnY5QiKQCwdsKMlQA/##ALLOWED_ORIGINS=https://osherboudara.com,https://www.osherboudara.com" \
  --set-secrets="ANTHROPIC_API_KEY=anthropic-api-key:latest,GITHUB_KEY=github-key:latest"
```

Verify the env landed as intended — this catches the comma problem immediately:

```bash
gcloud run services describe "$SERVICE" --region="$REGION" \
  --format='value(spec.template.spec.containers[0].env)'
```

Notes:
- `--min-instances=0` is the whole point — no traffic, no charge. Cold start is
  ~1–2s for this image (341 MB, no torch).
- `ALLOWED_ORIGINS` **must** list the real site origins or the browser will block
  every API call with a CORS error. No trailing slash. `curl` will keep working
  regardless, which makes this failure mode confusing — always test in a browser.
- `GOOGLE_DOC_ABOUTME_URL` — add it here too if you want about-me pulled live.
- Rate limiting is per-instance, so the effective ceiling is
  `CHAT_RATE_LIMIT × max-instances`.

Smoke-test the deployed service:

```bash
URL=$(gcloud run services describe "$SERVICE" --region="$REGION" --format='value(status.url)')
curl "$URL/health"
curl -N -X POST "$URL/api/chat" -H 'content-type: application/json' \
  -d '{"message":"What does Osher do at Cognizant?"}'
```

## 5. Frontend on Cloudflare Pages

Connect the GitHub repo in the Cloudflare dashboard (Workers & Pages → Create →
Pages → Connect to Git), then:

| Setting | Value |
|---|---|
| Production branch | `main` |
| Root directory | `frontend` |
| Build command | `npm run build` |
| Output directory | `dist` |
| Node version | 22 (env var `NODE_VERSION=22`) |

Add a build environment variable — **start with the raw Cloud Run URL**:

```
VITE_API_BASE_URL = https://osher-ai-twin-xxxxxxxx-uw.a.run.app
```

This is baked in at build time, so **changing it requires a rebuild**, not just a
redeploy.

Get the site working on the `*.pages.dev` + `*.run.app` pair first, end to end. Only
then attach custom domains. Debugging CORS, DNS, and TLS simultaneously is how a
one-hour deploy becomes a weekend.

## 6. Domains

- **Apex + www → Pages.** In Pages → Custom domains, add `osherboudara.com` and
  `www.osherboudara.com`. If DNS is already on Cloudflare this is automatic;
  otherwise move the nameservers first.
- **`api.osherboudara.com` → Cloud Run.** Cloud Run domain mappings are only
  available in some regions and require verifying domain ownership first
  (`gcloud domains verify osherboudara.com`, via Search Console):

  ```bash
  gcloud beta run domain-mappings create \
    --service="$SERVICE" --domain=api.osherboudara.com --region="$REGION"
  ```

  Set the record it gives you to **DNS-only (grey cloud)** in Cloudflare — proxying
  in front of Cloud Run's managed cert breaks the issuance handshake.

  *If mapping isn't available in your region,* the `*.run.app` URL is perfectly fine
  to keep using. It's stable and TLS-terminated; only the address bar is uglier, and
  no visitor ever sees it.

Whenever the API host changes, update `VITE_API_BASE_URL` **and** `ALLOWED_ORIGINS`,
then rebuild Pages. These two must always agree — most post-deploy breakage is a
mismatch between them.

## 7. Cutover and teardown

Only after the new site is verified end-to-end:

1. Point DNS fully at Pages, confirm chat / projects / resume / certs all work.
2. **Stop, then delete the Lightsail instance** (stop first — a day of "is anything
   still calling it?" is cheap insurance) and release its static IP, or it keeps billing.
3. Delete the keep-alive Lambda + its EventBridge schedule (`old_lambda_function/`).
   Cloud Run scales to zero, so nothing needs pinging.
4. ✅ Done — removed the dead Streamlit surface from the repo: `Home.py`, `pages/`,
   `chatbot/`, `db/`, `update.py`, `utils/`, `.streamlit/`, root `pyproject.toml` /
   `uv.lock`, plus `old_lambda_function/`, `app_thumbnail.png`, and the
   Streamlit-only `.devcontainer/`.
5. Set a **monthly spend cap** in the Anthropic Console, and a GCP budget alert.

## Expected cost

| Item | Cost |
|---|---|
| Cloud Run | ~$0 idle; a portfolio's traffic sits inside the free tier |
| Artifact Registry | ~$0.10/GB/month (one 341 MB image) |
| Cloudflare Pages | Free |
| Anthropic (Haiku 4.5) | ~$0.001–0.006 per question |

Versus a Lightsail instance at $5–10/month running 24/7 to serve almost no traffic.
