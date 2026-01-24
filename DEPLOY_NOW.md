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
2. Wait for build to finish (~2–3 min). Uses a slim image (< 4 GB); embeddings and sentiment run via Hugging Face API.
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


## 📝 Quick Reference

**Railway Backend:**
- URL: `https://your-app.up.railway.app`
- Health: `/health`
- API: `/api/v1/emails/analyze`

**Vercel Frontend:**
- URL: `https://your-app.vercel.app`
- Calls Railway backend automatically

