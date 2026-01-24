# 🚀 Deployment Checklist - Railway + Vercel

## ✅ Pre-Deployment Checklist

Before deploying, make sure:

- [ ] Code is pushed to GitHub (public or private repo)
- [ ] `.env` is NOT committed (check `.gitignore`)
- [ ] Backend builds locally: `docker build -t test .` (optional test)
- [ ] Frontend builds locally: `cd frontend && npm run build` (optional test)
- [ ] You have all API keys ready:
  - [ ] Supabase URL + Key
  - [ ] Pinecone API Key + Environment
  - [ ] Hugging Face API Key

---

## 📦 Step 1: Push to GitHub

```bash
# Make sure you're in the project root
cd "/Users/sidaksingh/Desktop/COMP9417/Main files/Machine Learning/project/new"

# Check what will be committed (make sure .env is NOT listed)
git status

# If you haven't initialized git yet:
git init
git add .
git commit -m "Initial commit: Email Prioritizer"
git branch -M main

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

**Important**: Verify `.env` is NOT in `git status` output!

---

## 🚂 Step 2: Deploy Backend to Railway

### 2.1 Create Railway Account & Project

1. Go to **[railway.app](https://railway.app)**
2. Sign in with **GitHub**
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your repository
6. Railway will auto-detect the Dockerfile

### 2.2 Set Environment Variables

In Railway dashboard → Your Project → **Variables** tab, add:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=email-prioritizer
HUGGINGFACE_API_KEY=your_hf_key
ENVIRONMENT=production
```

**Where to find these:**
- **Supabase**: Dashboard → Settings → API → URL and anon key
- **Pinecone**: Dashboard → API Keys → copy key and environment
- **Hugging Face**: Settings → Access Tokens → create new token

### 2.3 Deploy & Get URL

1. Railway will automatically start building (watch the logs)
2. Once built, go to **Settings** → **Networking**
3. Click **"Generate Domain"**
4. Copy the URL (e.g., `https://email-prioritizer-production.up.railway.app`)

### 2.4 Test Backend

```bash
curl https://your-railway-url.up.railway.app/health
```

Should return: `{"status":"healthy","timestamp":...}`

**Save this URL** - you'll need it for Vercel!

---

## ⚡ Step 3: Deploy Frontend to Vercel

### 3.1 Create Vercel Account & Project

1. Go to **[vercel.com](https://vercel.com)**
2. Sign in with **GitHub**
3. Click **"Add New"** → **"Project"**
4. Import your GitHub repository
5. **Important**: Set **Root Directory** to `frontend`
6. Framework: **Next.js** (auto-detected)

### 3.2 Set Environment Variables

In Vercel → Your Project → **Settings** → **Environment Variables**, add:

```
NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app
```

**Use the Railway URL from Step 2.3!**

Select environments: **Production**, **Preview**, **Development**

### 3.3 Deploy

1. Click **"Deploy"**
2. Vercel will build and deploy automatically
3. Once done, you'll get a URL like `https://your-project.vercel.app`

### 3.4 Test Frontend

1. Open your Vercel URL
2. Try **"Analyze email"** - should work!
3. Try **"Connect inbox"** - should connect to your Railway backend

---

## 🎉 Step 4: Verify Everything Works

### Test Backend
```bash
curl https://your-railway-url.up.railway.app/health
curl https://your-railway-url.up.railway.app/api/v1/emails/analyze \
  -X POST -H "Content-Type: application/json" \
  -d '{"subject":"Test","sender":"test@example.com","recipient":"you@example.com","body":"Test email","received_at":"2024-01-15T10:00:00"}'
```

### Test Frontend
- Open Vercel URL
- Analyze an email → should get priority score
- Connect inbox → should fetch and analyze emails

---

## 🔧 Troubleshooting

### Backend Issues

**Build fails:**
- Check Railway logs → Build tab
- Verify all env vars are set
- Check Dockerfile is in repo root

**Runtime errors:**
- Check Railway logs → Deployments tab
- Verify Supabase/Pinecone/HF keys are correct
- Check `/health` endpoint

**Port issues:**
- Railway auto-sets `PORT` env var
- Dockerfile uses `${PORT:-8000}` - should work

### Frontend Issues

**"API unavailable":**
- Check `NEXT_PUBLIC_API_URL` in Vercel env vars
- Must be the Railway URL (with `https://`)
- Rebuild after changing env vars

**CORS errors:**
- Backend allows `*` origins - should work
- If issues, check Railway logs

**Build fails:**
- Check Vercel build logs
- Verify `frontend/` is set as root directory
- Try `npm run build` locally first

---

## 📝 Quick Commands Reference

```bash
# Test backend locally
curl http://localhost:8000/health

# Test backend deployed
curl https://your-railway-url.up.railway.app/health

# Check Railway logs
# (In Railway dashboard → Deployments → View logs)

# Check Vercel logs
# (In Vercel dashboard → Deployments → View logs)
```

---

## 🎯 Next Steps After Deployment

1. ✅ Test all features work
2. ✅ Share your Vercel URL in portfolio/resume
3. ✅ Monitor Railway usage (free tier: $5 credit/month)
4. ✅ Optional: Add custom domain
5. ✅ Update README with live URLs

---

**You're ready to deploy! 🚀**
