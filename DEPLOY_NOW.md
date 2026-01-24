# 🚀 Deploy Now: Railway + Vercel (Step-by-Step)

Follow these steps in order. Takes ~15 minutes.

---

## 📋 Step 1: Push Code to GitHub

### 1.1 Initialize Git (if not done)

```bash
cd "/Users/sidaksingh/Desktop/COMP9417/Main files/Machine Learning/project/new"

# Check if .env is ignored (should NOT appear in git status)
git status | grep .env
# Should show nothing (or "nothing to commit")

# If .env shows up, it's NOT ignored - DON'T commit it!
```

### 1.2 Create GitHub Repo

1. Go to [github.com](https://github.com) → **New repository**
2. Name it: `email-prioritizer` (or any name)
3. **Don't** initialize with README (you already have files)
4. Click **Create repository**

### 1.3 Push Your Code

```bash
# In your project directory
git init
git add .
git commit -m "Initial commit: Email Prioritizer"

# Add your GitHub repo (replace YOUR_USERNAME and YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

**⚠️ Important**: Before pushing, verify `.env` is NOT in the commit:
```bash
git status
# .env should NOT be listed
```

---

## 🚂 Step 2: Deploy Backend to Railway

### 2.1 Create Railway Project

1. Go to **[railway.app](https://railway.app)**
2. Sign in with **GitHub**
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your `email-prioritizer` repo
6. Railway will auto-detect your Dockerfile ✅

### 2.2 Add Environment Variables

In Railway → Your Project → **Variables** tab, click **"New Variable"** and add these **one by one**:

| Variable Name | Value |
|---------------|--------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase anon key |
| `PINECONE_API_KEY` | Your Pinecone API key |
| `PINECONE_ENVIRONMENT` | e.g. `us-east-1` |
| `PINECONE_INDEX_NAME` | `email-prioritizer` |
| `HUGGINGFACE_API_KEY` | Your Hugging Face API token |
| `ENVIRONMENT` | `production` |

**Copy these from your local `.env` file (never commit .env).**

### 2.3 Deploy & Get URL

1. Railway will **automatically start building** (watch the **Deployments** tab)
2. Wait for build to finish (2-5 minutes - downloading models)
3. Once **"Active"**, go to **Settings** → **Networking**
4. Click **"Generate Domain"**
5. **Copy the URL** (e.g., `https://email-prioritizer-production.up.railway.app`)

### 2.4 Test Backend

Open the URL in browser or run:
```bash
curl https://your-railway-url.up.railway.app/health
```

Should show: `{"status":"healthy","timestamp":...}`

**✅ Save this Railway URL - you need it for Vercel!**

---

## ⚡ Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Project

1. Go to **[vercel.com](https://vercel.com)**
2. Sign in with **GitHub**
3. Click **"Add New"** → **"Project"**
4. Import your `email-prioritizer` repo
5. **IMPORTANT**: Click **"Edit"** next to Root Directory
6. Set Root Directory to: **`frontend`**
7. Framework: **Next.js** (auto-detected) ✅

### 3.2 Add Environment Variable

In Vercel → Your Project → **Settings** → **Environment Variables**:

1. Click **"Add New"**
2. Name: `NEXT_PUBLIC_API_URL`
3. Value: `https://your-railway-url.up.railway.app` (paste your Railway URL from Step 2.3)
4. Select: **Production**, **Preview**, **Development**
5. Click **"Save"**

### 3.3 Deploy

1. Click **"Deploy"** button
2. Vercel will build automatically (1-2 minutes)
3. Once done, you'll get a URL like `https://email-prioritizer.vercel.app`

### 3.4 Test Frontend

1. Open your Vercel URL
2. Try **"Analyze email"** → should work! ✅
3. Try **"Connect inbox"** → should connect to Railway backend ✅

---

## 🎉 Done!

Your app is now live:
- **Backend**: `https://your-app.up.railway.app`
- **Frontend**: `https://your-app.vercel.app`

---

## 🔧 If Something Goes Wrong

### Backend not working?

1. Check Railway **Deployments** → **View Logs**
2. Look for errors (missing env vars, import errors, etc.)
3. Verify all 7 environment variables are set correctly
4. Check `/health` endpoint works

### Frontend can't connect to backend?

1. Check `NEXT_PUBLIC_API_URL` in Vercel env vars = your Railway URL
2. Must start with `https://` (not `http://`)
3. Rebuild Vercel after changing env vars (Settings → Redeploy)

### Build fails?

**Backend (Railway):**
- Check Dockerfile is in repo root
- Check `requirements.txt` exists
- Check logs for specific error

**Frontend (Vercel):**
- Check Root Directory = `frontend`
- Check `frontend/package.json` exists
- Try building locally: `cd frontend && npm run build`

---

## 📝 Quick Reference

**Railway Backend:**
- URL: `https://your-app.up.railway.app`
- Health: `/health`
- API: `/api/v1/emails/analyze`

**Vercel Frontend:**
- URL: `https://your-app.vercel.app`
- Calls Railway backend automatically

---

**Ready? Start with Step 1! 🚀**
