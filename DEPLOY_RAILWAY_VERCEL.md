# Deploy Email Prioritizer: Railway (Backend) + Vercel (Frontend)

## Overview

- **Backend (FastAPI)**: Railway  
- **Frontend (Next.js)**: Vercel  
- **Real email**: IMAP inbox connect (Gmail app password, etc.)

---

## 1. Deploy Backend to Railway

### 1.1 Create Railway project

1. Go to [railway.app](https://railway.app) and sign in (e.g. GitHub).
2. **New Project** → **Deploy from GitHub repo**.
3. Select your repo. If the app is in a subfolder, set **Root Directory** to that folder (or repo root if backend is at root).
4. Railway will detect the **Dockerfile** and use it.

### 1.2 Configure build

- **Builder**: Dockerfile (auto-detected).
- **Dockerfile path**: `Dockerfile` (project root).

### 1.3 Set environment variables

In **Project → Variables**, add (values from your `.env`):

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase anon key |
| `PINECONE_API_KEY` | Pinecone API key |
| `PINECONE_ENVIRONMENT` | e.g. `us-east-1` |
| `PINECONE_INDEX_NAME` | e.g. `email-prioritizer` |
| `HUGGINGFACE_API_KEY` | Hugging Face API key |
| `ENVIRONMENT` | `production` |

Optional: `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN` if you use Gmail OAuth later.

### 1.4 Deploy and get URL

1. Trigger a deploy (push to main or manual deploy).
2. Open **Settings → Networking → Generate Domain**.
3. Copy the URL, e.g. `https://your-app.up.railway.app`.

### 1.5 Check backend

```bash
curl https://your-app.up.railway.app/health
# Expect: {"status":"healthy","timestamp":...}
```

---

## 2. Deploy Frontend to Vercel

### 2.1 Create Vercel project

1. Go to [vercel.com](https://vercel.com) and sign in (e.g. GitHub).
2. **Add New** → **Project** → import your repo.
3. Set **Root Directory** to `frontend` (where the Next.js app lives).
4. **Framework Preset**: Next.js (auto-detected).

### 2.2 Set environment variables

In **Project → Settings → Environment Variables** add:

| Name | Value | Env |
|------|--------|-----|
| `NEXT_PUBLIC_API_URL` | `https://your-app.up.railway.app` | Production, Preview |

Use your real Railway backend URL from step 1.4.

### 2.3 Deploy

1. **Deploy**. Vercel builds and deploys the Next.js app.
2. Open the Vercel URL, e.g. `https://your-project.vercel.app`.

### 2.4 Check frontend

- Open the Vercel URL.
- Use **Analyze email**, **Connect inbox**, and **Generate response**.
- **Connect inbox** calls the backend `/api/v1/emails/fetch` (IMAP). Ensure your backend URL is correct and CORS allows the Vercel origin (your backend currently allows `*`).

---

## 3. Connect real email (IMAP)

### Gmail

1. Enable **2-Factor Authentication** on your Google account.
2. **Google Account → Security → 2-Step Verification → App passwords**.
3. Create an app password for “Mail” (or “Other”).
4. In the frontend **Connect inbox** tab, use:
   - **Email**: your Gmail address.
   - **App password**: the 16-character app password (no spaces).

### Other providers

- **Outlook/Hotmail**: use account email + app password (or normal password if no 2FA).
- **Yahoo**: use email + app password.

The app uses IMAP (e.g. `imap.gmail.com` for Gmail) and fetches recent emails, then analyzes them via your backend.

---

## 4. Monorepo layout

If your repo looks like:

```
your-repo/
├── Dockerfile          # Backend
├── requirements.txt
├── backend/
├── frontend/           # Next.js
├── .env                # local only, not committed
└── ...
```

- **Railway**: root = repo root, build = Dockerfile.
- **Vercel**: root = `frontend`.

---

## 5. Optional: custom domains

- **Railway**: Settings → Networking → Custom Domain.
- **Vercel**: Project Settings → Domains.

Update `NEXT_PUBLIC_API_URL` if you switch the backend to a custom domain.

---

## 6. Troubleshooting

| Issue | Check |
|-------|--------|
| Backend 500 / startup errors | Railway logs; env vars (Supabase, Pinecone, Hugging Face). |
| Frontend “API unavailable” | `NEXT_PUBLIC_API_URL` = Railway URL; CORS on backend (already `*`). |
| IMAP “fetch failed” | Correct email + app password; 2FA + app password for Gmail; no typos. |
| Build fails (backend) | Dockerfile build logs; `requirements.txt` and system deps. |
| Build fails (frontend) | Vercel build logs; `npm run build` in `frontend` locally. |

---

## 7. Quick reference

- **Backend**: Railway, Dockerfile, `/health`, `/api/v1/...`.
- **Frontend**: Vercel, `frontend/`, `NEXT_PUBLIC_API_URL` → Railway URL.
- **IMAP**: Gmail (or other) app password in **Connect inbox**.
